# Installation Guide

## Prerequisites
- Python 3.9+
- Docker and Docker Compose
- Node.js 16+ (for frontend development)
- Neo4j 5.0+ (automatically installed via Docker)

## Quick Start

### Windows
1. Clone the repository
2. Navigate to the project directory
3. Run `scripts\setup_windows.bat` or `scripts\setup_windows.ps1`
4. Copy `example.env` to `.env` and configure your settings
5. Start development server with `scripts\development.bat`

### Linux/Mac
1. Clone the repository
2. Navigate to the project directory
3. Make scripts executable: `chmod +x scripts/*.sh`
4. Run `scripts/setup.sh`
5. Copy `example.env` to `.env` and configure your settings
6. Start development server with `scripts/development.sh`

## Virtual Environment

The project uses Python's built-in venv module for dependency isolation. The virtual environment is automatically:
- Created in `.venv` directory during setup
- Added to `.gitignore` to prevent committing
- Activated when running development scripts

To manually activate the virtual environment:

Windows (CMD):
```cmd
.venv\Scripts\activate.bat
```

Windows (PowerShell):
```powershell
.venv\Scripts\Activate.ps1
```

Linux/Mac:
```bash
source .venv/bin/activate
```

You'll know it's activated when you see (.venv) at the start of your command prompt.

## Docker Setup

1. Ensure Docker and Docker Compose are installed
2. Run `docker-compose up -d`
3. Access Neo4j browser at http://localhost:7474

## Neo4j Configuration

1. Wait for Neo4j container to start (~30 seconds)
2. Set password in `.env` file (NEO4J_PASSWORD)
3. Database will be automatically initialized

## Verification

1. Access the application at `http://localhost:5000`
2. Verify database connection at `http://localhost:5000/api/status`
3. Check the debug panel at `http://localhost:5000/debug`

## Common Issues

### Virtual Environment

If you see "Virtual environment not found":
1. Delete `.venv` directory if it exists
2. Run appropriate setup script again
3. Check Python version (3.9+ required)

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

## Development Workflow

1. Activate virtual environment (done automatically by development scripts)
2. Make your changes
3. Run tests: `pytest`
4. Submit pull request

## Next Steps

1. Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
2. Set up your IDE with project settings
3. Configure Git hooks for code quality checks