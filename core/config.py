import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigError(Exception):
    """Raised when application configuration cannot be loaded safely."""


ROOT_DIR = Path(__file__).resolve().parents[1]
SECRETS_FILE = ROOT_DIR / "secrets.json"
REQUIRED_SECRET_KEYS = ("APP_KEY", "APP_SECRET", "ACCOUNT_NO")


def load_secrets(file_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load and validate secrets with fail-fast error handling."""
    # 1. Streamlit Cloud의 st.secrets 확인
    try:
        import streamlit as st
        # st.secrets에 모든 필수 키가 있는지 확인
        if all(key in st.secrets for key in REQUIRED_SECRET_KEYS):
            return {
                "APP_KEY": st.secrets["APP_KEY"],
                "APP_SECRET": st.secrets["APP_SECRET"],
                "ACCOUNT_NO": st.secrets["ACCOUNT_NO"],
                "MOCK": st.secrets.get("MOCK", False)
            }
    except Exception:
        pass # 로컬 환경에서 Streamlit 없이 실행하거나, 시크릿이 없을 때는 파일 읽기로 넘어감

    # 2. 로컬의 secrets.json 파일 읽기
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
