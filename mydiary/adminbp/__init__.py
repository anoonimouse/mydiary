from flask import Blueprint
admin_bp = Blueprint("adminbp", __name__, template_folder="../templates/admin", static_folder="../static")
