from flask import render_template
from mydiary.main import bp

@bp.route('/')
def index():
    return render_template('home.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/safety')
def safety():
    return render_template('safety.html')

@bp.route('/blog')
def blog():
    return render_template('blog.html')
