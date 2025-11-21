from flask import Blueprint

bp = Blueprint('inbox', __name__)

from mydiary.inbox import routes
