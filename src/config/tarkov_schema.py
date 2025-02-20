import os  # Add this import statement
from typing import Dict, Any, Optional
import requests
from src.config.config import Config
from src.config.queries import ITEMS_QUERY, ITEM_BY_ID_QUERY

class GraphQLClient:
    def __init__(self, endpoint: Optional[str] = None):
        self.session = requests.Session()
        self._endpoint = endpoint or Config.GRAPHQL_ENDPOINT

    def execute_query(self, query: Optional[str] = None, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GraphQL query and return response"""
        query = query or ITEMS_QUERY
        variables = variables or {}
        
        response = self.session.post(
            self._endpoint,
            json={'query': query, 'variables': variables},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()

    def fetch_items(self, lang: str = 'en', item_ids: Optional[list] = None) -> Dict[str, Any]:
        """Fetch items from Tarkov API"""
        variables = {'lang': lang}
        if item_ids:
            variables['ids'] = ','.join(item_ids)
        return self.execute_query(ITEMS_QUERY, variables)

    def fetch_item(self, item_id: str, lang: str = 'en') -> Dict[str, Any]:
        """Fetch a single item by ID"""
        variables = {'id': item_id, 'lang': lang}
        return self.execute_query(ITEM_BY_ID_QUERY, variables)

def save_schema_documentation(output_path: str = "docs/schema.md") -> None:
    """Fetch and save API schema documentation as Markdown"""
    schema_query = """
    query {
      __schema {
        types {
          name
          description
          fields {
            name
            description
            type {
              name
              ofType {
                name
              }
            }
            args {
              name
              description
              type {
                name
              }
            }
          }
        }
      }
    }
    """
    
    client = GraphQLClient()
    result = client.execute_query(query=schema_query)
    
    # Generate markdown
    markdown = ["# Tarkov.dev API Schema Documentation\n"]
    
    for type_info in result["data"]["__schema"]["types"]:
        # Skip internal GraphQL types
        if type_info["name"].startswith("__"):
            continue
            
        markdown.append(f"## {type_info['name']}\n")
        if type_info.get("description"):
            markdown.append(f"{type_info['description']}\n")
            
        if type_info.get("fields"):
            markdown.append("### Fields\n")
            for field in type_info["fields"]:
                field_type = field["type"]["name"] or field["type"]["ofType"]["name"]
                markdown.append(f"#### {field['name']}: {field_type}")
                if field.get("description"):
                    markdown.append(f"\n{field['description']}")
                markdown.append("\n")
                
                if field["args"]:
                    markdown.append("\nArguments:\n")
                    for arg in field["args"]:
                        markdown.append(f"- {arg['name']}: {arg['type']['name']}")
                        if arg.get("description"):
                            markdown.append(f"\n  {arg['description']}")
                    markdown.append("\n")
            markdown.append("\n---\n")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown))