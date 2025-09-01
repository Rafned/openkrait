import logging
import os
import re
from config import Config

Config.load()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def optimize_pipeline(pipeline_path, platform="auto"):
    """
    Функция для анализа и оптимизации CI/CD pipeline файлов.
    - Санитизирует путь (abspath, check isfile).
    - Авто-детект платформы по имени/пути.
    - Проверяет наличие caching/parallel.
    """
    try:
        pipeline_path = os.path.abspath(pipeline_path)
        if not os.path.isfile(pipeline_path):
            raise ValueError(f"Pipeline file {pipeline_path} not found or not a file.")

        with open(pipeline_path, 'r', encoding='utf-8') as f:
            pipeline = f.read()

        if platform == "auto":
            basename = os.path.basename(pipeline_path)
            dirname = os.path.dirname(pipeline_path)
            if "Jenkinsfile" in basename:
                platform = "jenkins"
            elif ".gitlab-ci.yml" in basename:
                platform = "gitlab"
            elif ".github/workflows" in dirname:
                platform = "github"
            else:
                raise ValueError("Could not detect platform. Specify explicitly: jenkins, gitlab, github.")

        lower_pipeline = pipeline.lower()
        if platform == "jenkins":
            if "cache" not in lower_pipeline and "stash" not in lower_pipeline:
                logging.info("Recommendation: enable caching with 'cache' or 'stash' in Jenkinsfile.")
            else:
                logging.info("Caching already in use. For advanced optimization, consider Pro version.")
        elif platform == "gitlab":
            if "cache" not in lower_pipeline and "parallel" not in lower_pipeline:
                logging.info("Recommendation: enable caching with 'cache' or parallel execution with 'parallel' in .gitlab-ci.yml.")
            else:
                logging.info("Optimization detected. For advanced optimization, consider Pro version.")
        elif platform == "github":
            if "cache" not in lower_pipeline and "strategy" not in lower_pipeline:
                logging.info("Recommendation: enable caching with 'cache' or strategy with 'strategy' in workflow.yml.")
            else:
                logging.info("Caching/strategy already in use. For advanced optimization, consider Pro version.")
        else:
            raise ValueError("Platform not supported.")

    except Exception as e:
        logging.error(f"Error analyzing pipeline: {str(e)}")
        raise  # Поднимаем исключение для тестов

if __name__ == "__main__":
    optimize_pipeline('Jenkinsfile')