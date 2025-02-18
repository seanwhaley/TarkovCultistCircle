# Building and Launching the TarkovCultistCircle Web Application

This document outlines the steps required to build and launch the TarkovCultistCircle web application using Docker Compose.

## Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Node.js](https://nodejs.org/) (for local development)

## Steps

1. **Clone the Repository:**

    ```bash
    git clone <repository_url>
    cd TarkovCultistCircle
    ```

2. **Configure the .env File:**

    - Create a `.env` file in the root directory of the project.
    - Populate the `.env` file with the necessary environment variables:

        ```properties
        # Database Configuration
        NEO4J_URI=bolt://neo4j:7687
        NEO4J_USER=neo4j
        NEO4J_PASSWORD=your_secure_password
        NEO4J_DATABASE=neo4j

        # API Configuration
        GRAPHQL_ENDPOINT=https://api.tarkov.dev/graphql
        
        # Web Application
        PORT=3000
        NODE_ENV=production
        ```

3. **Build and Launch the Application:**

    ```bash
    docker-compose up --build
    ```

    This command will:
    - Build the TypeScript application
    - Start the Neo4j database
    - Launch the web server
    - Set up the development environment

4. **Access the Web Application:**

    - Main application: `http://localhost:3000`
    - Neo4j Browser: `http://localhost:7474`

## Development Setup

For local development:

```bash
npm install
npm run dev
```

## Project Structure

TarkovCultistCircle/
├── src/                  # Source code
├── dist/                 # Compiled JavaScript
├── docs/                 # Documentation
├── tests/               # Test files
├── docker-compose.yml   # Docker composition
├── Dockerfile           # Container definition
├── .env                # Environment variables
└── package.json        # Dependencies

## Troubleshooting

- Check container logs: `docker-compose logs`
- Ensure all ports are available
- Verify Neo4j credentials
- Check network connectivity to api.tarkov.dev

## Data Persistence

- Neo4j data is stored in a named volume
- Database backups can be created using Neo4j's backup tools
