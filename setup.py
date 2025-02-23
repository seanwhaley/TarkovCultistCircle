from setuptools import setup, find_packages

setup(
    name="tarkovcultistcircle",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        "": ["py.typed"],
    },
    install_requires=[
        "flask",
        "flask-cors",
        "flask-graphql",
        "flask-jwt-extended",
        "neo4j",
        "psutil>=5.9.0",
        "python-dotenv",
    ],
    python_requires=">=3.8",
)
