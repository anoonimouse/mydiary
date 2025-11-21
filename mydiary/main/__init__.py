from flask import Blueprint

bp = Blueprint('main', __name__)

from mydiary.main import routes
