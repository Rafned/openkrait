import logging
import os
import re  # Добавь этот импорт!
import subprocess
from pathlib import Path
from kubernetes import client, config
from .config import Config

class ConfigurationError(Exception):
    """Базовое исключение для ошибок конфигурации."""
    pass

Config.load()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scan_k8s_resources():
    """
    Основная функция для сканирования Kubernetes ресурсов.
    - Загружает config безопасно (in-cluster или из файла с проверкой существования).
    - Инициализирует API client без request_timeout (удален для совместимости с kubernetes==29.0.0).
    - Получает pods, configmaps, secrets с лимитом (100), чтобы предотвратить DoS.
    - Сканирует pods на уязвимые images (пример: nginx:1.14), интегрирует Trivy если доступен.
    - Для ConfigMaps: Проверяет на sensitive keys без раскрытия данных.
    - Для Secrets: Только метаданные, без чтения содержимого.
    - Обработка ошибок: Логирует только str(e), без traceback для security.
    """
    try:
        # Загрузка конфигурации
        if os.getenv('K8S_IN_CLUSTER', 'false').lower() == 'true':
            config.load_incluster_config()
        else:
            kube_config_path = os.path.expanduser('~/.kube/config')
            if not os.path.isfile(kube_config_path):
                raise ValueError("Kubernetes config file not found or invalid.")
            # ВАЖНО: Добавляем проверку прав доступа
            if not os.access(kube_config_path, os.R_OK):
                raise ConfigurationError("Kubeconfig file is not readable. Check permissions.")
            config.load_kube_config(config_file=kube_config_path)

        # Инициализация API-клиента без request_timeout
        v1 = client.CoreV1Api(api_client=client.ApiClient())

        # Получение ресурсов с лимитом (anti-DoS)
        pods = v1.list_pod_for_all_namespaces(limit=100).items
        config_maps = v1.list_config_map_for_all_namespaces(limit=100).items
        secrets = v1.list_secret_for_all_namespaces(limit=100).items

        # Сканирование подов
        for pod in pods:
            for container in pod.spec.containers:
                image = container.image
                if not image or not isinstance(image, str):
                    continue
                
                # Проверяем уязвимые образы из конфига
                vuln_images = Config.get("vulnerability.images", [])
                for vuln in vuln_images:
                    if re.match(vuln["pattern"], image):  # Используем re.match
                        logging.warning(f"Detected vulnerable image {image} in pod {pod.metadata.name}. Recommendation: {vuln['recommendation']} | Severity: {vuln['severity']}")
                        break  # Прерываем цикл после первого совпадения
                
                # Интеграция с Trivy
                trivy_path = '/usr/local/bin/trivy'  # Определяем путь здесь
                if os.path.isfile(trivy_path) and os.access(trivy_path, os.X_OK):
                    try:
                        result = subprocess.run([trivy_path, 'image', image], capture_output=True, text=True, check=True, timeout=60)
                        if "VULNERABILITY" in result.stdout:
                            logging.warning(f"Trivy scan for {image} in pod {pod.metadata.name}: Vulnerabilities found (details in Trivy output).")
                    except subprocess.SubprocessError as e:
                        logging.error(f"Trivy execution error: {str(e)}")
                else:
                    logging.info("Trivy not found or not executable. Skipping scan.")

        # Сканирование ConfigMap
        for cm in config_maps:
            if cm.data and any(key.lower() == 'password' for key in cm.data.keys()):
                logging.warning(f"In ConfigMap {cm.metadata.name} detected sensitive field. Recommendation: move to Secret")

        # Сканирование Secrets
        for secret in secrets:
            logging.info(f"Secret {secret.metadata.name} found. Recommendation: ensure encryption at rest.")

    except Exception as e:
        logging.error(f"Error during scanning: {str(e)}")
        raise  # Поднимаем исключение для тестов

if __name__ == "__main__":
    scan_k8s_resources()
