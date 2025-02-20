import requests

def fetch_tarkov_dev_data(query: str) -> dict:
    """Fetch data from Tarkov API using GraphQL query."""
    url = "https://api.tarkov.dev/graphql"
    headers = {"Content-Type": "application/json"}
    payload = {"query": query}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return {"status_code": response.status_code, "response": response.json()}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
