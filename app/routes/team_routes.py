from flask import Blueprint, render_template, session, redirect, url_for, request
from app.models import Teams
from app import db

bp = Blueprint('team', __name__)


@bp.route('/team_stats', methods=['GET', 'POST'])
def team_stats():
    if "username" in session:
        if request.method == 'POST':
            team_name = request.form.get('team_name')
            year = request.form.get('year')

            team_info = Teams.query.filter_by(team_name=team_name, yearID=year).first()

            return render_template("team_stats.html", team_info=team_info, team_name=team_name, year=year)

        return render_template("team_form.html")
    return redirect(url_for('main.home'))