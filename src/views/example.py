from flask import Blueprint

example_blueprint = Blueprint('example', __name__)

@example_blueprint.route('/example')
def example_route():
    return 'This is an example route'
