import pytest
import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from pipeline_optimizer import optimize_pipeline

@pytest.fixture
def setup_logging(caplog):
    caplog.set_level(logging.INFO)
    return caplog

@pytest.fixture
def temp_file(tmp_path):
    """Создает временный файл для тестов."""
    file = tmp_path / "Jenkinsfile"
    return file

def test_pipeline_optimizer_missing_file(setup_logging):
    """Тест: Файл pipeline не существует."""
    with pytest.raises(ValueError, match="Pipeline file .* not found"):
        optimize_pipeline("/nonexistent")
    assert "Error analyzing pipeline" in setup_logging.text

def test_pipeline_optimizer_jenkins_no_cache(temp_file, setup_logging):
    """Тест: Jenkinsfile без cache/stash."""
    temp_file.write_text("pipeline { stages { stage('Build') {} } }", encoding='utf-8')
    optimize_pipeline(str(temp_file), platform="jenkins")
    assert "Recommendation: enable caching with 'cache' or 'stash'" in setup_logging.text

def test_pipeline_optimizer_gitlab_with_cache(temp_file, setup_logging):
    """Тест: .gitlab-ci.yml с cache."""
    temp_file.write_text("stages:\n  - build\ncache: {}\n", encoding='utf-8')
    optimize_pipeline(str(temp_file), platform="gitlab")
    assert "Optimization detected" in setup_logging.text