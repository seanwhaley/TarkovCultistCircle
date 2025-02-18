# TarkovCultistCircle

This project is a Python-based web application designed to interact with the [Tarkov API](https://api.tarkov.dev/graphql), store item data in a Neo4j database, and provide optimization and tracking features.

## Key Features

- **Flask Web Framework** for the website interface
- **Neo4j** chosen as the graph database for its rich relationship management
- **Docker Compose** for containerizing both the application and database
- **Environment Variables** for secure configuration management
- **Material Design** for the user interface
- **Automated Testing** for core features
- **Comprehensive Documentation**

## Prerequisites

- Docker and Docker Compose
- Python 3.9+ (optional, for local development)
- Git

## Quick Start

1. Clone this repository
2. Set up environment variables:

   ```bash
   cp example.env .env
   # Edit .env with your configuration
   ```

3. Start the application:

   ```bash
   docker-compose up --build
   ```

4. Visit `http://localhost:5000`

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| FLASK_SECRET_KEY | Flask session secret | `random_string_here` |
| NEO4J_PASSWORD | Database password | `your_secure_password` |
| DOCKER_NEO4J_AUTH | Neo4j auth string | `neo4j/your_password` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| FLASK_ENV | development | Flask environment |
| FLASK_DEBUG | 1 | Enable debug mode |
| NEO4J_URI | bolt://localhost:7687 | Neo4j connection URI |
| NEO4J_USER | neo4j | Neo4j username |

## Project Structure

```text
TarkovCultistCircle/
├── templates/           # HTML templates
├── static/             # Static assets (CSS, JS, images)
├── src/                # Python source code
│   ├── app.py         # Flask application
│   ├── db.py          # Database operations
│   └── routes.py      # Route definitions
├── docs/              # Documentation
│   ├── DB_STRUCTURE.md
│   └── GRAPHQL_QUERIES.md
├── tests/             # Test files
├── docker-compose.yml # Docker configuration
├── Dockerfile         # Application container definition
├── requirements.txt   # Python dependencies
└── example.env        # Environment template
```

## Documentation

- [Database Structure](docs/DB_STRUCTURE.md)
- [GraphQL Queries](docs/GRAPHQL_QUERIES.md)

## Development Setup

1. Create virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start Neo4j:

   ```bash
   docker-compose up neo4j_db
   ```

4. Run Flask:

   ```bash
   flask run
   ```

## Testing

Run the test suite:

   ```bash
   python -m pytest
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
