import os
import sys
import pytest
from click.testing import CliRunner
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src/openkrait'))
#from openkrait.cli import main
from openkrait.cli import main
#sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.mark.integration
def test_cli_help():
    """Smoke-test: проверяем, что CLI запускается и показывает справку."""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert "Usage" in result.output
