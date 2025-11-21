from flask import Blueprint

bp = Blueprint('auth', __name__)

from mydiary.auth import routes
