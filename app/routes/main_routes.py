from flask import Blueprint, render_template, session, redirect, url_for

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    if "username" in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@bp.route('/dashboard')
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session['username'])
    return redirect(url_for('main.home'))

@bp.route('/team_stats')
def team_stats():
    if "username" in session:
        return render_template("team_stats.html")
    return redirect(url_for('main.home'))
