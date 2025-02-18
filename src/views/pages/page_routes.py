from flask import Blueprint, render_template, current_app
from src.core.graphql import GraphQLClient

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    """Main page view"""
    return render_template('pages/index.html')

@pages_bp.route('/optimizer')
def optimizer():
    """Optimizer page view"""
    return render_template('pages/optimizer.html')

@pages_bp.route('/analysis')
def analysis():
    """Analysis page view"""
    return render_template('pages/analysis.html')

@pages_bp.route('/history')
def history():
    """History page view"""
    return render_template('pages/history.html')
