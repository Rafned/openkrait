from setuptools import setup, find_packages

setup(
    name="open_krait",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "open_krait=cli:main"
        ]
    },
    install_requires=[
        "hvac==2.3.0", 
        "pyyaml==6.0.1",
        "kubernetes==29.0.0",
        "click"
    ],
    extras_require={
        "dev": ["pytest==7.2.0", "flake8==6.0.0"]
    },
    data_files=[("/etc/bash_completion.d", ["open_krait-completion.bash"])],
    author="DenFar",
    description="open_krait is open source project",
    url="https://github.com/your-username/open_krait"
)