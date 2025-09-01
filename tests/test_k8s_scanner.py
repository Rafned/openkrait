import pytest
import logging
import sys
import os
from unittest.mock import MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from k8s_scanner import scan_k8s_resources
from kubernetes import client

@pytest.fixture
def setup_logging(caplog):
    """Настройка caplog для проверки логов."""
    caplog.set_level(logging.INFO)
    return caplog

def test_k8s_scanner_config_missing(mocker, setup_logging):
    """Тест: Отсутствие kube config файла."""
    mocker.patch('os.getenv', return_value='false')
    mocker.patch('os.path.isfile', return_value=False)
    mocker.patch('os.access', return_value=True)
    with pytest.raises(ValueError, match="Kubernetes config file not found or invalid"):
        scan_k8s_resources()
    assert "Error during scanning" in setup_logging.text

def test_k8s_scanner_vulnerable_image(mocker, setup_logging):
    """Тест: Обнаружение уязвимого образа nginx:1.14."""
    pod = MagicMock()
    pod.metadata.name = "test-pod"
    pod.spec.containers = [MagicMock(image="nginx:1.14")]
    mocker.patch('os.getenv', return_value='false')
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('kubernetes.config.load_kube_config')
    mocker.patch('os.access', return_value=True)
    v1_mock = mocker.patch('kubernetes.client.CoreV1Api')
    v1_mock.return_value.list_pod_for_all_namespaces.return_value.items = [pod]
    v1_mock.return_value.list_config_map_for_all_namespaces.return_value.items = []
    v1_mock.return_value.list_secret_for_all_namespaces.return_value.items = []
    subprocess_mock = mocker.patch('subprocess.run')
    subprocess_mock.return_value.stdout = "Some fake trivy output"
    subprocess_mock.return_value.returncode = 0
    
    scan_k8s_resources()
    assert "Detected vulnerability in image nginx:1.14" in setup_logging.text

def test_k8s_scanner_trivy_not_found(mocker, setup_logging):
    """Тест: Trivy отсутствует."""
    pod = MagicMock()
    pod.metadata.name = "test-pod"
    pod.spec.containers = [MagicMock(image="nginx:latest")]
    mocker.patch('os.getenv', return_value='false')
    mocker.patch('os.path.isfile', side_effect=[True, False])  # kube config есть, trivy нет
    mocker.patch('kubernetes.config.load_kube_config')
    mocker.patch('os.access', return_value=True)
    v1_mock = mocker.patch('kubernetes.client.CoreV1Api')
    v1_mock.return_value.list_pod_for_all_namespaces.return_value.items = [pod]
    v1_mock.return_value.list_config_map_for_all_namespaces.return_value.items = []
    v1_mock.return_value.list_secret_for_all_namespaces.return_value.items = []
    scan_k8s_resources()
    assert "Trivy not found or not executable" in setup_logging.text

def test_k8s_scanner_sensitive_configmap(mocker, setup_logging):
    """Тест: Обнаружение password в ConfigMap."""
    config_map = MagicMock()
    config_map.metadata.name = "test-cm"
    config_map.data = {"password": "secret"}
    mocker.patch('os.getenv', return_value='false')
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('kubernetes.config.load_kube_config')
    mocker.patch('os.access', return_value=True)
    v1_mock = mocker.patch('kubernetes.client.CoreV1Api')
    v1_mock.return_value.list_pod_for_all_namespaces.return_value.items = []
    v1_mock.return_value.list_config_map_for_all_namespaces.return_value.items = [config_map]
    v1_mock.return_value.list_secret_for_all_namespaces.return_value.items = []
    scan_k8s_resources()
    assert "In ConfigMap test-cm detected sensitive field" in setup_logging.text