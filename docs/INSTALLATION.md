# Installation Guide

This guide will help you set up the Tarkov Cultist Circle application on your system.

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose
- Node.js and npm (for frontend development)
- Git

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/TarkovCultistCircle.git
cd TarkovCultistCircle
```

### 2. Set Up Python Environment

Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_SECRET_KEY=your_secret_key
NEO4J_URI=bolt://neo4j_db:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
GRAPHQL_ENDPOINT=https://api.tarkov.dev/graphql
```

### 4. Set Up Docker Containers

Build and start the containers:

```bash
docker-compose up --build -d
```

### 5. Initialize the Database

Run the database initialization script:

```bash
flask init-db
```

### 6. Load Initial Data

Ingest data from the Tarkov API:

```bash
flask ingest-data
```

## Verification

1. Access the application at `http://localhost:5000`
2. Verify database connection at `http://localhost:5000/api/status`
3. Check the debug panel at `http://localhost:5000/debug`

## Common Issues

### Database Connection

If you cannot connect to Neo4j:
1. Ensure Neo4j container is running
2. Check Neo4j credentials in `.env`
3. Wait for Neo4j to fully initialize (may take a minute)

### API Data Ingestion

If data ingestion fails:
1. Verify internet connection
2. Check Tarkov API endpoint status
3. Review logs for specific error messages

## Troubleshooting Guide

### Database Issues

#### Neo4j Connection Problems
```
Error: Unable to connect to Neo4j database
```
Solutions:
1. Check container status:
   ```bash
   docker ps | grep neo4j
   ```
2. Verify port availability:
   ```bash
   netstat -an | grep 7687
   ```
3. Check Neo4j logs:
   ```bash
   docker-compose logs neo4j
   ```
4. Verify memory allocation is sufficient:
   - Minimum 2GB for Neo4j container
   - Check docker-compose.yml settings

#### Data Import Failures
```
Error: Failed to import initial dataset
```
Solutions:
1. Check disk space
2. Verify Neo4j write permissions
3. Increase Neo4j heap size in docker-compose.yml
4. Clear Neo4j data and retry:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Python Environment Issues

#### Package Installation Failures
```
Error: Could not install packages due to an OSError
```
Solutions:
1. Upgrade pip:
   ```bash
   python -m pip install --upgrade pip
   ```
2. Install build dependencies:
   - Windows: Install Visual C++ build tools
   - Linux: `apt-get install python3-dev build-essential`
3. Clear pip cache:
   ```bash
   pip cache purge
   ```

#### Virtual Environment Problems
```
Error: No module named venv
```
Solutions:
1. Windows:
   ```bash
   py -m pip install --user virtualenv
   ```
2. Linux/MacOS:
   ```bash
   sudo apt-get install python3-venv  # Ubuntu/Debian
   brew install python3-venv  # MacOS
   ```

### Docker-Related Issues

#### Container Startup Failures
```
Error: Container exited with non-zero status
```
Solutions:
1. Check container logs:
   ```bash
   docker-compose logs --tail=100 service_name
   ```
2. Verify port conflicts:
   ```bash
   docker-compose ps
   ```
3. Check resource limits:
   ```bash
   docker stats
   ```

#### Volume Mount Issues
```
Error: Unable to mount volume
```
Solutions:
1. Check permissions:
   ```bash
   ls -la ./neo4j/data
   ```
2. Clean up old volumes:
   ```bash
   docker-compose down -v
   docker volume prune
   ```

### API Integration Issues

#### GraphQL Connection Failures
```
Error: Unable to fetch data from Tarkov API
```
Solutions:
1. Verify API status:
   ```bash
   curl https://api.tarkov.dev/graphql -X POST -H "Content-Type: application/json"
   ```
2. Check rate limits
3. Verify network connectivity
4. Use VPN if region-blocked

#### Data Synchronization Problems
```
Error: Data sync incomplete or corrupted
```
Solutions:
1. Clear local cache:
   ```bash
   flask clear-cache
   ```
2. Verify data schema version
3. Run manual sync:
   ```bash
   flask sync-data --force
   ```

### Platform-Specific Notes

#### Windows
- Enable WSL2 for better Docker performance
- Configure line endings:
  ```bash
  git config --global core.autocrlf input
  ```
- Add Python to PATH during installation
- Use PowerShell in Admin mode for permissions

#### MacOS
- Install Homebrew first:
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- Install dependencies:
  ```bash
  brew install python docker docker-compose node
  ```
- Grant necessary permissions to Docker

#### Linux
- Add user to docker group:
  ```bash
  sudo usermod -aG docker $USER
  ```
- Install system dependencies:
  ```bash
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install -y python3-pip python3-dev
  ```

### Development Environment Issues

#### Hot Reload Not Working
Solutions:
1. Check file watchers limit (Linux):
   ```bash
   echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```
2. Verify debug mode is enabled
3. Check for syntax errors blocking reload

#### Test Suite Failures
Solutions:
1. Verify test database is configured
2. Check test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```
3. Run with verbose output:
   ```bash
   python -m pytest -v
   ```

## Development Setup

For development work:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m unittest discover tests

# Start development server
flask run --debug
```

## Health Checks

### Verify Complete Installation
```bash
flask verify-install
```

### Check System Requirements
```bash
flask system-check
```

### Validate Configuration
```bash
flask config-check
```

## Performance Optimization

### Production Deployment
1. Enable production mode:
   ```bash
   export FLASK_ENV=production
   ```
2. Configure gunicorn workers
3. Set up reverse proxy (nginx/apache)
4. Enable database connection pooling

### Memory Usage
- Monitor Neo4j heap usage
- Configure Python garbage collection
- Set appropriate cache sizes
- Monitor Docker resource limits

## Next Steps

- Review the [API Documentation](API_REFERENCE.md)
- Check the [Contributing Guidelines](CONTRIBUTING.md)
- Explore the [Component Library](components.md)