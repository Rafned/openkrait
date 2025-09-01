import sys
import logging
import click
import functools 
from k8s_scanner import scan_k8s_resources
from pipeline_optimizer import optimize_pipeline
from log_analyzer import analyze_logs
from secret_manager import store_secret
from config import Config

Config.load()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def safe_command_executor(command_func, *args, **kwargs):
    """Выполняет команду CLI, отлавливает исключения и красиво выходит."""
    try:
        return command_func(*args, **kwargs)
    except Exception as e:
        click.echo(click.style(f"ERROR: {str(e)}", fg='red'), err=True)
        logging.exception("Command failed")
        sys.exit(1)

#  Создаем группу main и применяем кастомный command
@click.group()
def main():
    """OpenKrait CLI - маленький помощник, который работает, пока вы спите."""
    pass



#  объявляем команды 
@main.command()
def scan_k8s():
    """Scan Kubernetes resources."""
    safe_command_executor(lambda: scan_k8s_resources())
    click.echo("Scan completed successfully!")

@main.command()
@click.option('--pipeline', required=True, help='Path to pipeline file')
@click.option('--platform', default='auto', help='Platform: jenkins, gitlab, github')
def optimize_pipeline_cmd(pipeline, platform): 
    """Optimize CI/CD pipeline."""
    safe_command_executor(lambda:optimize_pipeline(pipeline, platform))
    click.echo("Optimization completed!")

@main.command()
@click.option('--log-path', required=True, help='Path to log file')
def analyze_logs_cmd(log_path):
    """Analyze logs from file."""
    safe_command_executor(lambda:analyze_logs(source='file', log_path=log_path)) 
    click.echo('Log analysis completed successfully!')

@main.command()
@click.option('--secret', required=True, help='Secret to store in Vault') 
def store_secret_cmd(secret):
    """Store secret in HashiCorp Vault."""
    safe_command_executor(lambda:store_secret(secret))
    click.echo('Secret stored successfully!')


@main.command()
def store_secret_stdin():
    """Store secret from stdin (safe for scripts)."""
    secret = click.get_text_stream('stdin').read().strip()
    if not secret:
        raise ValueError("No secret provided via stdin")
    safe_command_executor(lambda:store_secret(secret))
    click.echo('Secret from stdin stored successfully!')

if __name__ == "__main__":
    main()