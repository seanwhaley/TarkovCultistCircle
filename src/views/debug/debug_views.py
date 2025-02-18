from flask import render_template, jsonify
from src.core.graphql import GraphQLClient
from src.config import Config
from src.core.database import Neo4jDB
from src.utils.storage import response_storage
from datetime import datetime

def debug_panel_view():
    """Render the debug panel"""
    return render_template('debug/index.html',
                         graphql_endpoint=Config.GRAPHQL_ENDPOINT,
                         neo4j_uri=Config.NEO4J_URI)

def test_connection_view():
    """Test database and GraphQL connections"""
    try:
        # Test Neo4j connection
        db = Neo4jDB()
        with db.get_session() as session:
            neo4j_status = session.run("RETURN 1 as test").single()['test'] == 1
        
        # Test GraphQL connection
        client = GraphQLClient()
        graphql_result = client.execute_query()
        graphql_status = 'items' in graphql_result.get('data', {})
        
        return jsonify({
            'neo4j': neo4j_status,
            'graphql': graphql_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def fetch_graphql_view():
    try:
        client = GraphQLClient()
        result = client.execute_query()
        
        # Check for error in fetch result
        if 'errors' in result:
            return jsonify({
                "success": False,
                "message": "GraphQL request failed",
                "details": {
                    "error": result['errors'],
                    "request": {
                        "time": datetime.utcnow().isoformat() + 'Z',
                        "endpoint": Config.GRAPHQL_ENDPOINT,
                        "query": Config.GRAPHQL_QUERY
                    }
                }
            }), 400
            
        # Process successful response
        response_data = result.get('data', {})
        if not response_data or 'items' not in response_data:
            return jsonify({
                "success": False,
                "message": "Invalid GraphQL response format",
                "details": {
                    "response": result,
                    "request": {
                        "time": datetime.utcnow().isoformat() + 'Z',
                        "endpoint": Config.GRAPHQL_ENDPOINT,
                        "query": Config.GRAPHQL_QUERY
                    }
                }
            }), 400

        # Save response
        response_storage.save_response(response_data)

        return jsonify({
            "success": True,
            "message": "Successfully fetched data",
            "details": {
                "request": {
                    "time": datetime.utcnow().isoformat() + 'Z',
                    "endpoint": Config.GRAPHQL_ENDPOINT,
                    "query": Config.GRAPHQL_QUERY
                },
                "response": response_data
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Unexpected error occurred",
            "details": {
                "error": str(e),
                "type": type(e).__name__,
                "request": {
                    "time": datetime.utcnow().isoformat() + 'Z',
                    "endpoint": Config.GRAPHQL_ENDPOINT,
                    "query": Config.GRAPHQL_QUERY
                    
                }
            }
        }), 500

def load_last_response_view():
    response = response_storage.load_latest_response()
    if response:
        return jsonify({
            'success': True,
            'response': response
        })
    return jsonify({
        'success': False,
        'error': 'No saved response found'
    }), 404

def test_neo4j_view():
    try:
        db = Neo4jDB()
        with db.get_session() as session:
            result = session.run("RETURN 1 as test")
            return jsonify({
                'success': True,
                'message': 'Successfully connected to Neo4j',
                'details': {
                    'connection': 'Active',
                    'query_test': 'Passed'
                }
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to connect to Neo4j',
            'details': {
                'error': str(e),
                'type': type(e).__name__
            }
        }), 500

def import_last_response_view():
    response = response_storage.load_latest_response()
    if not response:
        return jsonify({
            'success': False,
            'message': 'No saved response found to import'
        }), 404
        
    if 'data' not in response or 'items' not in response['data']:
        return jsonify({
            'success': False,
            'message': 'Invalid response format'
        }), 400
        
    db = Neo4jDB()
    #items = response['data']['items']
    #if save_items_to_neo4j(items):
    #    return jsonify({
    #        'success': True,
    #        'message': 'Successfully imported items to Neo4j',
    #        'details': {
    #            'itemCount': len(items),
    #            'timestamp': datetime.utcnow().isoformat()
    #        }
    #    })
    
    #return jsonify({
    #    'success': False,
    #    'message': 'Failed to import items to Neo4j'
    #}), 500
    
    items = response['data']['items']
    #if save_items_to_neo4j(items):
    return jsonify({
        'success': True,
        'message': 'Successfully imported items to Neo4j',
        'details': {
            'itemCount': len(items),
            'timestamp': datetime.utcnow().isoformat()
        }
    })
    
    return jsonify({
        'success': False,
        'message': 'Failed to import items to Neo4j'
    }), 500
