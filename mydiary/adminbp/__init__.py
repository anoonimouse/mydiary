from flask import Blueprint

bp = Blueprint('adminbp', __name__)

from mydiary.adminbp import routes
