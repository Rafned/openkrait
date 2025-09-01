import pytest
import logging
import sys
import os
from unittest.mock import MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from log_analyzer import analyze_logs


@pytest.fixture
def setup_logging(caplog):
    """Настройка caplog для проверки логов."""
    caplog.set_level(logging.INFO)
    return caplog

@pytest.fixture
def temp_log_file(tmp_path):
    """Создает временный лог-файл."""
    file = tmp_path / "test.log"
    file.write_text("test log content\n", encoding='utf-8')  
    return file

def test_log_analyzer_missing_file(setup_logging, mocker):
    mocker.patch('log_analyzer.safe_path', side_effect=lambda path, base: path)
    """Тест: Лог-файл не существует."""
    with pytest.raises(ValueError, match="Log file .* not found or not a file"):
        analyze_logs("file", log_path="/nonexistent")
    assert "Error analyzing logs" in setup_logging.text

def test_log_analyzer_error_log(temp_log_file, mocker, setup_logging):
    mocker.patch('log_analyzer.safe_path', side_effect=lambda path, base: path)
    """Тест: Лог содержит ERROR, но не логируется полностью (CWE-532)."""
    temp_log_file.write_text("ERROR: something bad password=secret\n", encoding='utf-8')
    analyze_logs("file", log_path=str(temp_log_file))
    assert "Detected issue: error or warning found in log" in setup_logging.text
    assert "password=secret" not in setup_logging.text  # Проверка CWE-532 fix

def test_log_analyzer_too_large_file(temp_log_file, mocker, setup_logging):
    """Тест: Лог-файл слишком большой."""
    mocker.patch('log_analyzer.safe_path', side_effect=lambda path, base: path)
    mocker.patch('os.path.getsize', return_value=11 * 1024 * 1024)  # >10MB
    with pytest.raises(ValueError, match="Log file too large"):
        analyze_logs("file", log_path=str(temp_log_file))
    assert "Error analyzing logs" in setup_logging.text