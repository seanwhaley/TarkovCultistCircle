# Tarkov Cultist Circle

A lightweight Tarkov item optimizer using Flask and Neo4j.

## Architecture

- **Web Framework**: Flask
- **Database**: Neo4j
- **Rate Limiting**: In-memory implementation
- **Caching**: Neo4j native query caching
- **UI**: Material Design

## Design Principles

- Simplicity first: Single framework, minimal dependencies
- In-memory solutions where possible
- Vertical scaling
- Built for small to medium user base

## Features

- Item optimization
- Market analysis
- Price tracking
- Simple rate limiting
- JWT authentication
- GraphQL client for Tarkov.dev API

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (copy example.env to .env)

3. Start Neo4j:
```bash
docker-compose up -d neo4j
```

4. Run the application:
```bash
flask run
```

## Development

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/api/index.md)
- [Database Structure](docs/DB_STRUCTURE.md)

## Performance

The application is optimized for:
- Up to 1000 concurrent users
- 100k+ items in database
- Sub-100ms API responses
- Efficient item relationship traversal

## Support

See [SUPPORT.md](docs/SUPPORT.md) for support options.

## License

This project is licensed under the terms found in [LICENSE.md](docs/LICENSE.md).
