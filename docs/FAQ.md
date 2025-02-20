# Frequently Asked Questions (FAQ)

## General

### What is Tarkov Cultist Circle?

Tarkov Cultist Circle is a Flask-based web application that uses a Neo4j database for data storage. The application is containerized using Docker and Docker Compose, and it includes various features such as authentication, API endpoints, and item management.

### How do I set up the application?

Please refer to the [Installation Instructions](INSTALLATION.md) for detailed setup instructions.

## Troubleshooting

### I encountered an error during installation. What should I do?

If you encounter any issues during installation, please refer to the [Installation Instructions](INSTALLATION.md) and ensure that all prerequisites are met. If the issue persists, please open an issue on GitHub.

### How do I run the tests?

To run the tests, use the following command:

```bash
python -m unittest discover tests
```

### How do I ingest data from the Tarkov API?

To ingest data from the Tarkov API, use the following command:

```bash
flask ingest-data
```

## Contribution

### How can I contribute to the project?

Please refer to the [Contributing Guidelines](CONTRIBUTING.md) for information on how to contribute to the project.
