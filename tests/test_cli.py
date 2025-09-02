import pytest
import logging
import sys
import os
from unittest.mock import patch

#sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src/openkrait'))
from openkrait.cli import main

@pytest.fixture
def setup_logging(caplog):
    caplog.set_level(logging.INFO)
    return caplog

def test_cli_scan_k8s(mocker, setup_logging):
    mocker.patch("openkrait.cli.scan_k8s_resources")
    
    with patch.object(sys, 'argv', ["cli.py", "scan-k8s"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

def test_cli_store_secret_stdin(mocker, setup_logging):
    mocker.patch("openkrait.cli.store_secret")
    mocker.patch("openkrait.cli.sys.stdin.read", return_value="mysecret\n")
    
    with patch.object(sys, 'argv', ["cli.py", "store-secret-stdin"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
