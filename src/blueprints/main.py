from flask import Blueprint, render_template
from flask_login import login_required
from src.core.cache import cached
from src.types.responses import ResponseType

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@cached(timeout=300)
def index() -> ResponseType:
    return render_template('pages/home/index.html')

@main_bp.route('/about')
def about() -> ResponseType:
    return render_template('pages/about/index.html')

@main_bp.route('/contact')
def contact() -> ResponseType:
    return render_template('pages/contact/index.html')
