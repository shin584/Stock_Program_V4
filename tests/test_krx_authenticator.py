from unittest.mock import patch

import pytest

from Stock_Program_V4.core.krx_authenticator import (
    KRXAuthenticationError,
    KRXAuthenticator,
)


def test_krx_authenticator_reads_credentials_from_environment():
    with patch.dict(
        "os.environ",
        {"KRX_ID": "test-user", "KRX_PW": "test-password"},
        clear=True,
    ):
        authenticator = KRXAuthenticator(env_loader=lambda: None)

    assert authenticator.krx_id == "test-user"
    assert authenticator.krx_pw == "test-password"


def test_krx_authenticator_raises_when_credentials_are_missing():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(KRXAuthenticationError) as exc_info:
            KRXAuthenticator(env_loader=lambda: None)

    assert "KRX 자격 증명이 환경 변수에 설정되지 않았습니다." in str(exc_info.value)
