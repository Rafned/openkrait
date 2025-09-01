import pytest
import logging
import sys
import os
from unittest.mock import MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from secret_manager import store_secret

@pytest.fixture
def setup_logging(caplog):
    caplog.set_level(logging.INFO)
    return caplog

def test_secret_manager_no_token(mocker, setup_logging):
    """Тест: Отсутствие VAULT_TOKEN."""
    mocker.patch("os.getenv", side_effect=lambda x, y=None: None if x == "VAULT_TOKEN" else y)
    with pytest.raises(ValueError, match="VAULT_TOKEN not set"):
        store_secret("test-secret")
    assert "Error storing secret" in setup_logging.text

def test_secret_manager_limit_reached(mocker, setup_logging):
    """Тест: Достигнут лимит секретов."""
    mocker.patch("os.getenv", side_effect=lambda x, y=None: "token" if x == "VAULT_TOKEN" else "5" if x == "MAX_SECRETS" else y)
    client_mock = MagicMock()
    client_mock.secrets.kv.v2.list_secrets.return_value = {"data": {"keys": ["s1", "s2", "s3", "s4", "s5"]}}
    mocker.patch("hvac.Client", return_value=client_mock)
    store_secret("test-secret")
    assert "Secret limit (5) reached" in setup_logging.text