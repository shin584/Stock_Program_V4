import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigError(Exception):
    """Raised when application configuration cannot be loaded safely."""


ROOT_DIR = Path(__file__).resolve().parents[1]
SECRETS_FILE = ROOT_DIR / "secrets.json"
REQUIRED_SECRET_KEYS = ("APP_KEY", "APP_SECRET", "ACCOUNT_NO")


def load_secrets(file_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load and validate secrets.json with fail-fast error handling."""
    secrets_path = Path(file_path) if file_path is not None else SECRETS_FILE

    if not secrets_path.exists():
        raise ConfigError(f"Secrets file not found: {secrets_path}")

    try:
        with secrets_path.open("r", encoding="utf-8") as handle:
            secrets = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Secrets file contains invalid JSON: {secrets_path}") from exc
    except OSError as exc:
        raise ConfigError(f"Unable to read secrets file: {secrets_path}") from exc

    if not isinstance(secrets, dict):
        raise ConfigError("Secrets file must contain a JSON object.")

    missing_keys = [
        key for key in REQUIRED_SECRET_KEYS if not str(secrets.get(key, "")).strip()
    ]
    if missing_keys:
        raise ConfigError(f"Missing required secret keys: {', '.join(missing_keys)}")

    return secrets


def get_kis_config() -> Dict[str, Any]:
    """Return KIS client settings using the validated secrets file."""
    secrets = load_secrets()
    return {
        "app_key": secrets["APP_KEY"],
        "app_secret": secrets["APP_SECRET"],
        "acc_no": secrets["ACCOUNT_NO"],
        "mock": bool(secrets.get("MOCK", True)),
    }
