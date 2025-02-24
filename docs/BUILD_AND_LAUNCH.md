# Build and Launch Guide

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Neo4j (or Docker)

## Environment Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment file:
```bash
cp example.env .env
```

Edit .env with your configuration values.

## Database Setup

### Using Docker (Recommended)
```bash
docker-compose up -d neo4j
```

### Manual Neo4j Setup
1. Install Neo4j from https://neo4j.com/download/
2. Configure password and update .env
3. Start Neo4j service

## Running the Application

### Development
```bash
flask run --debug
```

### Production
```bash
gunicorn wsgi:app
```

## Configuration

Key environment variables:
- `FLASK_ENV`: development/production
- `NEO4J_URI`: Database connection URI
- `NEO4J_USER`: Database username
- `NEO4J_PASSWORD`: Database password
- `SECRET_KEY`: Application secret key
- `RATE_LIMIT_ENABLED`: Enable/disable rate limiting
- `RATE_LIMIT_DEFAULT`: Default requests per hour
- `RATE_LIMIT_WINDOW`: Time window in seconds

## Health Checks

1. Application: http://localhost:5000/health
2. Neo4j: http://localhost:7474

## Monitoring

Application metrics available at:
- `/metrics`: Basic application metrics
- `/status`: System status

## Deployment

### Docker Deploy
```bash
docker-compose up -d
```

### Manual Deploy
1. Set up Python environment
2. Configure Neo4j
3. Run with gunicorn
4. Set up reverse proxy (nginx recommended)

## Common Issues

### Database Connection
- Verify Neo4j is running
- Check connection string in .env
- Ensure correct credentials

### Performance
- Check Neo4j query logging
- Monitor memory usage
- Review rate limiting settings
- Optimize database indices

## Security Notes

- Always change default passwords
- Update SECRET_KEY in production
- Configure CORS appropriately
- Set secure headers in production
- Enable HTTPS in production
