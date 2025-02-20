# Tarkov Cultist Circle

## Overview

Tarkov Cultist Circle is a Flask-based web application that uses a Neo4j database for data storage. The application is containerized using Docker and Docker Compose, and it includes various features such as authentication, API endpoints, item management, and optimization.

## Setup Instructions

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/TarkovCultistCircle.git
    cd TarkovCultistCircle
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the environment variables in the `.env` file:
    ```env
    FLASK_SECRET_KEY=your_secret_key
    NEO4J_URI=bolt://neo4j_db:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=your_password
    GRAPHQL_ENDPOINT=https://api.tarkov.dev/graphql
    ```

5. Build and run the Docker containers:
    ```bash
    docker-compose up --build
    ```

6. Access the application at `http://localhost:5000`.

## Usage Instructions

* To run the tests:
    ```bash
    python -m unittest discover tests
    ```

* To run the application:
    ```bash
    flask run
    ```

* To ingest data from the Tarkov API:
    ```bash
    flask ingest-data
    ```

## Sitemap and Functionality

### Main Routes (127.0.0.1:5000)
/ - Home page (Main index) `main_bp`
- Basic welcome page with navigation

### Authentication Routes
/login - Login page `auth_bp`
- Basic login functionality
/logout - Logout page
- Basic logout functionality

### Items Routes
/items/ - Items main page `items_bp`
- Lists available items
/items/api/list - Items API endpoint
- Returns JSON list of items
/items/price_override - (POST) Price override functionality
/items/blacklist_item - (POST) Item blacklisting
/items/lock_item - (POST) Item locking

### API Routes
/api/ - API index `api_bp`
- Returns operational status
/api/status - API status endpoint
- Returns database connection status

### Debug Interface
/debug - Debug panel
- GraphQL API testing
- Neo4j database connection testing
- Response visualization
- Import validation and control

### Optimizer Interface
/optimizer - Optimizer page
- Item combination optimization interface
- Price controls
- Item filtering

When accessing `127.0.0.1:5000`, you will be directed to the home page through the main blueprint's root route (/). The application uses Flask's blueprint system for modular routing, with each section of functionality organized into its own blueprint.

The templates follow a similar structure under `templates` with corresponding HTML files for each route. The base template (`base.html`) provides the common layout and styling used across all pages.

All routes are properly registered through the blueprint system in `__init__.py` and initialized in the Flask application factory function.

# Detailed Folder and File Structure

## `src/`

* `__init__.py`: Factory function to initialize the Flask app, register blueprints, and configure logging.
* `config.py`: Configuration classes for different environments.

## `src/blueprints/`

* `auth.py`: Authentication routes and logic.
* `main.py`: Main application routes.
* `api.py`: API routes and logic.
* `items.py`: Item-related routes.

## `src/views/`

* `other_file.py`: Contains utility functions used across the application.

## `tests/`

* `test_routes.py`: Unit tests for the Flask application routes.
* `test_models.py`: Unit tests for the Flask application models.
* `test_services.py`: Unit tests for the Flask application services.
* `test_utils.py`: Unit tests for the Flask application utility functions.
* `test_error_handling.py`: Unit tests for the Flask application error handling.
* `test_auth.py`: Unit tests for the Flask application authentication and authorization.
* `test_database.py`: Unit tests for the Flask application database interactions.
* `test_forms.py`: Unit tests for the Flask application form validation.

## `docs/`

* `README.md`: Setup and usage instructions.

## `Dockerfile`

* Ensure it is correctly set up to run the Flask application.

## `docker-compose.yml`

* Ensure it is correctly set up for multi-container setup with Neo4j and Flask.

## `.env`

* Ensure all sensitive information is stored in environment variables.