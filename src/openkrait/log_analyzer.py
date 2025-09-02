import logging
import os
import re
from sys import path
from pathlib import Path
from .config import Config

Config.load()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def safe_path(path, base="/app/logs"):
    resolved = Path(path).resolve()
    base_resolved = Path(base).resolve()
    if not str(resolved).startswith(str(base_resolved)):
        raise ValueError("Path traversal attempt detected.")
    return resolved

def analyze_logs(source, log_path=None, loki_url=None, es_host=None):
    """
    Функция для анализа логов из разных источников.
    - Для 'file': Санитизирует путь, проверяет размер (<10MB anti-DoS), читает строки.
    - Логирует без полного лога (omit for security, CWE-532 fix).
    - Для loki/es: Требует HTTPS, raises NotImplemented.
    """
    try:
        logs = []
        if source == 'file' and log_path:
            safe_log_path = safe_path(log_path, base="/app/logs")  
            if not os.path.isfile(safe_log_path):
                raise ValueError(f"Log file {safe_log_path} not found or not a file.")
            if os.path.getsize(safe_log_path) > 10 * 1024 * 1024:
                raise ValueError("Log file too large (>10MB).")
            with open(safe_log_path, 'r', encoding='utf-8') as f:
                logs = f.readlines()
        elif source == 'loki' and loki_url:
            if not loki_url.startswith('https://'):
                raise ValueError("Loki URL must use HTTPS.")
            raise NotImplementedError("Loki integration disabled for security; implement with auth.")
        elif source == 'elasticsearch' and es_host:
            if not es_host.startswith('https://'):
                raise ValueError("Elasticsearch host must use HTTPS.")
            raise NotImplementedError("Elasticsearch integration disabled for security; implement with auth.")
        else:
            raise ValueError("Specify correct source and parameters.")

        for log in logs:
            if re.search(r'error|warning', log, re.IGNORECASE):
                logging.warning("Detected issue: error or warning found in log (details omitted for security)")

    except Exception as e:
        logging.error(f"Error analyzing logs: {str(e)}")
        raise  # Поднимаем исключение для тестов


if __name__ == "__main__":
    analyze_logs('file', log_path='/path/to/log.log')
