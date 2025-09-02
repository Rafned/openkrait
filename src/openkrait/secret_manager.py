import logging
import os
import hvac
from .config import Config

Config.load()  
max_secrets = Config.get("limits", {}).get("max_secrets", 5)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def store_secret(secret, secret_path='my-secret'):
    """
    Функция для хранения секрета в HashiCorp Vault.
    - Берет token/url из env.
    - Требует HTTPS + SSL verify.
    - Проверяет лимит секретов.
    """
    try:
        vault_token = os.getenv('VAULT_TOKEN')
        vault_url = os.getenv('VAULT_URL', 'https://localhost:8200')
        if not vault_token:
            raise ValueError("Environment variable VAULT_TOKEN not set.")
        if not vault_url.startswith('https://'):
            raise ValueError("Vault URL must use HTTPS for security.")

        client = hvac.Client(url=vault_url, token=vault_token, verify=True)

        try:
            secrets_list = client.secrets.kv.v2.list_secrets(path='')['data']['keys']
        except hvac.exceptions.InvalidPath:
            secrets_list = []

        max_secrets = int(os.getenv('MAX_SECRETS', 5))
        if len(secrets_list) >= max_secrets:
            logging.warning(f"Secret limit ({max_secrets}) reached. Consider Pro version to remove limits.")
            return

        client.secrets.kv.v2.create_or_update_secret(path=secret_path, secret=dict(value=secret))
        logging.info(f"Secret stored in Vault at path {secret_path}")

    except Exception as e:
        logging.error(f"Error storing secret: {str(e)}")
        raise  # Поднимаем исключение для тестов

if __name__ == "__main__":
    store_secret('test-secret')
