# Tarkov Cultist Circle

A lightweight web application for optimizing Escape from Tarkov item combinations using Neo4j.

## Features

- Item combination optimization
- Price tracking
- Basic market data integration
- Simple Material Design UI

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

1. Clone the repository
2. Copy example.env to .env and configure
3. Run:
```bash
docker-compose up -d
```
4. Access at http://localhost:5000

## Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Testing

```bash
python -m pytest
```

### Project Structure

```
/
├── docker-compose.yml    # Container configuration
├── src/                  # Application code
│   ├── app.py           # Main Flask application
│   ├── models/          # Data models
│   ├── views/           # Route handlers
│   ├── static/          # CSS, JS files
│   └── templates/       # HTML templates
├── tests/               # Test cases
└── requirements.txt     # Python dependencies
```

### Documentation

Additional documentation has been consolidated here from the original multiple files. This simplified structure better matches the project scope and makes maintenance easier.

#### Database Schema

Neo4j graph structure:
- Items (nodes)
- Relationships (edges)
- Properties (name, price, etc.)

#### API Integration

Simplified integration with Tarkov.dev API for basic item data.

#### Contributing 

1. Fork the repository
2. Create feature branch
3. Submit pull request

Issues and feature requests are tracked in GitHub Issues, but given the project scope, expect focused updates primarily for:
- Bug fixes
- Essential features
- Critical security updates

## License

MIT License - See LICENSE file
