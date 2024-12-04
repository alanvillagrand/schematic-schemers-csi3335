from flask import Blueprint, render_template, session, redirect, url_for, request
from app.services.team_service import *

bp = Blueprint('team', __name__)


@bp.route('/team_stats', methods=['GET', 'POST'])
def team_stats():
    if "username" in session:
        if request.method == 'POST':
            team_name = request.form.get('team_name')
            year = request.form.get('year')

            team_info = get_team_info(team_name, year)
            batting_info = get_batting_info(team_name, year)
            pitching_info = get_pitching_info(team_name, year)
            batting_position_info = {
                "LF": get_position_info_playing_time('LF', team_name, year),
                "CF": get_position_info_playing_time('CF', team_name, year),
                "RF": get_position_info_playing_time('RF', team_name, year),
                "SS": get_position_info_playing_time('SS', team_name, year),
                "2B": get_position_info_playing_time('2B', team_name, year),
                "3B": get_position_info_playing_time('3B', team_name, year),
                "C": get_position_info_playing_time('C', team_name, year),
                "1B": get_position_info_playing_time('1B', team_name, year)
            }
            pitching_position_info = {
                "SP": get_pitching_info_playing_time('SP', team_name, year),
                "RP": get_pitching_info_playing_time('RP', team_name, year)
            }
            # if games started = 0, relif pitcher

            return render_template("team_stats.html",
                                   team_info=team_info,
                                   batting_info=batting_info,
                                   pitching_info=pitching_info,
                                   team_name=team_name,
                                   year=year,
                                   batting_position_info=batting_position_info,
                                   pitching_position_info=pitching_position_info)

        return render_template("team_form.html")
    return redirect(url_for('main.home'))

# @bp.route('/updatae_position_stats', methods=['GET'])
# def update_position_stats():
#     stat_type = request.args.get('stat_type')
#     category = request.args.get('category')

#     if category == "position-players":
#         if