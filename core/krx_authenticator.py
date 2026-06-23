from __future__ import annotations

import os
from typing import Callable

from dotenv import load_dotenv


class KRXAuthenticationError(ValueError):
    """Raised when KRX credentials or login session setup fails."""


class KRXAuthenticator:
    """Load KRX credentials and establish a pykrx authentication session."""

    def __init__(self, env_loader: Callable[[], object] = load_dotenv) -> None:
        env_loader()
        self._krx_id = os.environ.get("KRX_ID")
        self._krx_pw = os.environ.get("KRX_PW")

        if not self._krx_id or not self._krx_pw:
            raise KRXAuthenticationError(
                "KRX 자격 증명이 환경 변수에 설정되지 않았습니다."
            )

    @property
    def krx_id(self) -> str:
        return self._krx_id

    @property
    def krx_pw(self) -> str:
        return self._krx_pw

    def authenticate(self) -> None:
        try:
            from pykrx.website.comm.auth import build_krx_session, set_auth_session
        except ImportError as exc:
            raise KRXAuthenticationError("pykrx is not installed.") from exc

        session = build_krx_session(self._krx_id, self._krx_pw)
        if session is None:
            raise KRXAuthenticationError("KRX 인증에 실패했습니다.")

        set_auth_session(session)
