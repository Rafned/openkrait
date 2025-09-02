from setuptools import setup, find_packages

setup(
    name="openkrait",
    version="1.0.0",
    package_dir={"": "src"},  # Ищем пакеты в src/
    packages=find_packages(where="src"),  # Ищем пакеты в src/
    entry_points={
        "console_scripts": [
            "openkrait=openkrait.cli:main"  # Правильный путь к модулю
        ]
    },
    install_requires=[
        "hvac==2.3.0", 
        "pyyaml==6.0.1",
        "kubernetes==29.0.0",
        "click==8.0.0"
    ],
    author="Rafned",
    description="openkrait is open source project",
    url="https://github.com/Rafned/openkrait"
)
