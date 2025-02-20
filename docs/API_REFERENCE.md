# API Reference

## Authentication Endpoints

### `POST /login`

Authenticate a user and return a session token.

#### Request Body

```json
{
    "username": "your_username",
    "password": "your_password"
}
```

#### Response

```json
{
    "message": "Login successful",
    "token": "session_token"
}
```

### `GET /logout`

Log out a user and invalidate the session token.

#### Response

```json
{
    "message": "Logout successful"
}
```

## Item Endpoints

### `GET /items/api/list`

Retrieve a list of items.

#### Response

```json
{
    "items": [
        {
            "id": "item_id",
            "name": "item_name",
            "basePrice": "item_base_price",
            "lastLowPrice": "item_last_low_price",
            "avg24hPrice": "item_avg_24h_price",
            "updated": "item_updated_timestamp"
        }
    ]
}
```

### `POST /items/price_override`

Override the price of an item.

#### Request Body

```json
{
    "item_id": "item_id",
    "new_price": "new_price"
}
```

#### Response

```json
{
    "message": "Price override successful"
}
```

### `POST /items/blacklist_item`

Blacklist an item.

#### Request Body

```json
{
    "item_id": "item_id"
}
```

#### Response

```json
{
    "message": "Item blacklisted"
}
```

### `POST /items/lock_item`

Lock an item.

#### Request Body

```json
{
    "item_id": "item_id"
}
```

#### Response

```json
{
    "message": "Item locked"
}
```

## API Routes

### `GET /api/`

Retrieve the operational status of the API.

#### Response

```json
{
    "status": "operational"
}
```

### `GET /api/status`

Retrieve the database connection status.

#### Response

```json
{
    "status": "connected"
}
```

## Error Handling

### `404 Not Found`

#### Response

```json
{
    "error": "Not Found"
}
```

### `500 Internal Server Error`

#### Response

```json
{
    "error": "Internal Server Error"
}
```
````

### /d:/Users/crazy/OneDrive/Documents/GitHub/TarkovCultistCircle/docs/USAGE.md

Update the `USAGE.md` file to include detailed usage instructions and examples.

<file>
````markdown
// filepath: /d:/Users/crazy/OneDrive/Documents/GitHub/TarkovCultistCircle/docs/USAGE.md
# Usage Instructions

## Running the Application

To run the application, use the following command:

```bash
flask run
```

The application will be accessible at `http://localhost:5000`.

## Running Tests

To run the tests, use the following command:

```bash
python -m unittest discover tests
```

## Ingesting Data

To ingest data from the Tarkov API, use the following command:

```bash
flask ingest-data
```

## API Endpoints

The application provides several API endpoints. Here are some examples:

### Authentication

* **Login**: `POST /login`
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```

* **Logout**: `GET /logout`

### Items

* **List Items**: `GET /items/api/list`
    ```json
    {
        "items": [
            {
                "id": "item_id",
                "name": "item_name",
                "basePrice": "item_base_price",
                "lastLowPrice": "item_last_low_price",
                "avg24hPrice": "item_avg_24h_price",
                "updated": "item_updated_timestamp"
            }
        ]
    }
    ```

* **Price Override**: `POST /items/price_override`
    ```json
    {
        "item_id": "item_id",
        "new_price": "new_price"
    }
    ```

* **Blacklist Item**: `POST /items/blacklist_item`
    ```json
    {
        "item_id": "item_id"
    }
    ```

* **Lock Item**: `POST /items/lock_item`
    ```json
    {
        "item_id": "item_id"
    }
    ```

### API

* **API Index**: `GET /api/`
    ```json
    {
        "status": "operational"
    }
    ```

* **API Status**: `GET /api/status`
    ```json
    {
        "status": "connected"
    }
    ```

## Example Usage

Here are some examples of how to use the application:

### Example 1: Running the Application

1. Start the application:
    ```bash
    flask run
    ```

2. Open your browser and navigate to `http://localhost:5000`.

### Example 2: Running Tests

1. Run the tests:
    ```bash
    python -m unittest discover tests
    ```

2. Check the test results in the terminal.

### Example 3: Ingesting Data

1. Ingest data from the Tarkov API:
    ```bash
    flask ingest-data
    ```

2. Check the terminal for the ingestion status.
````

This completes the implementation of the actions based on the provided sitemap and functionality of the site. The documentation now includes detailed setup instructions, configuration details, usage instructions, API reference, development guidelines, testing instructions, contributing guidelines, changelog, license information, and a FAQ document. If there are any additional updates or specific areas you would like to review, please let me know!