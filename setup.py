"""Package setup configuration."""
from setuptools import setup, find_packages

setup(
    name="tarkovcultistcircle",
    version="0.1.0",
    description="A lightweight Tarkov item optimizer using Neo4j",
    packages=find_packages(),
    package_data={
        "": ["py.typed"],
    },
    python_requires=">=3.9",
    install_requires=[
        "flask",  # Web framework
        "flask-cors",  # Cross-origin resource sharing
        "flask-login",  # User session management
        "flask-jwt-extended",  # JWT authentication
        "neo4j",  # Graph database driver
        "python-dotenv",  # Environment configuration
        "psutil",  # Basic system monitoring
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "mypy",
            "black",
            "flake8",
            "isort",
            "types-flask",
            "types-flask-cors",
            "types-python-dotenv",
            "types-psutil",
        ]
    }
)
