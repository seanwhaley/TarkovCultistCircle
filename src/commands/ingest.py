import click
from flask.cli import with_appcontext
from src.utils.graphql import fetch_tarkov_dev_data
from src.db import get_db
from config.config import Config

@click.command('ingest-data')
@with_appcontext
def ingest_data_command():
    """Fetch data from Tarkov API and store in Neo4j."""
    click.echo('Fetching data from Tarkov API...')
    
    result = fetch_tarkov_dev_data(Config.GRAPHQL_QUERY)
    if 'error' in result:
        click.echo(f'Error fetching data: {result["error"]}')
        return
        
    if result['status_code'] != 200:
        click.echo(f'API returned status code: {result["status_code"]}')
        return
        
    data = result['response']
    if not data or 'data' not in data or 'items' not in data['data']:
        click.echo('Invalid response format')
        return
        
    items = data['data']['items']
    click.echo(f'Found {len(items)} items')
    
    db = get_db()
    try:
        # First, clean existing data
        db.query("MATCH (i:Item) DETACH DELETE i")
        
        # Create items
        for item in items:
            query = """
            CREATE (i:Item {
                id: $id,
                name: $name,
                basePrice: toString($basePrice),
                lastLowPrice: toString($lastLowPrice),
                avg24hPrice: toString($avg24hPrice),
                updated: $updated
            })
            """
            db.query(query, parameters=item)
            
        click.echo('Successfully ingested data into Neo4j')
    except Exception as e:
        click.echo(f'Error saving to Neo4j: {str(e)}')
    finally:
        if db:
            db.close()
