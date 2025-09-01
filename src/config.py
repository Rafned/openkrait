import yaml
from pathlib import Path

class Config:
    _cfg = None

    @classmethod
    def load(cls, path=None):
        config_path = Path(path or "config.yaml")
        if not config_path.exists():
            # Fallback to empty config if file doesn't exist yet
            cls._cfg = {}
            return
        cls._cfg = yaml.safe_load(config_path.read_text())

    @classmethod
    def get(cls, key, default=None):
        # Позволяет получать вложенные ключи через точку, например: "vulnerability.images"
        keys = key.split('.')
        value = cls._cfg
        for k in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(k, default)
        return value