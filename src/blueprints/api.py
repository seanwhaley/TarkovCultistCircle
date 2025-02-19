from flask import Blueprint

api_bp = Blueprint('api', __name__)

@api_bp.route('/data')
def get_data():
    return "Data Page"
