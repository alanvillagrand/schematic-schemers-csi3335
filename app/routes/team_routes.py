from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
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
                "LF": get_batting_position_info_playing_time('LF', team_name, year),
                "CF": get_batting_position_info_playing_time('CF', team_name, year),
                "RF": get_batting_position_info_playing_time('RF', team_name, year),
                "SS": get_batting_position_info_playing_time('SS', team_name, year),
                "2B": get_batting_position_info_playing_time('2B', team_name, year),
                "3B": get_batting_position_info_playing_time('3B', team_name, year),
                "C": get_batting_position_info_playing_time('C', team_name, year),
                "1B": get_batting_position_info_playing_time('1B', team_name, year)
            }
            pitching_position_info = {
                "SP": get_pitching_position_info_playing_time('SP', team_name, year),
                "RP": get_pitching_position_info_playing_time('RP', team_name, year)
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

@bp.route('/update_position_stats', methods=['GET'])
def update_position_stats():
    stat_type = request.args.get('stat_type')
    category = request.args.get('category')
    team_name = request.args.get('team_name')
    year = request.args.get('year')
    print(stat_type, category, team_name, year)

    if category == "position-players":
        if stat_type == "playing-time":
            updated_data = {
                "LF": get_batting_position_info_playing_time('LF', team_name, year),
                "CF": get_batting_position_info_playing_time('CF', team_name, year),
                "RF": get_batting_position_info_playing_time('RF', team_name, year),
                "SS": get_batting_position_info_playing_time('SS', team_name, year),
                "2B": get_batting_position_info_playing_time('2B', team_name, year),
                "3B": get_batting_position_info_playing_time('3B', team_name, year),
                "C": get_batting_position_info_playing_time('C', team_name, year),
                "1B": get_batting_position_info_playing_time('1B', team_name, year)
            }
        elif stat_type == "WAR":
            updated_data = {
                "LF": get_batting_position_info_WAR('LF', team_name, year),
                "CF": get_batting_position_info_WAR('CF', team_name, year),
                "RF": get_batting_position_info_WAR('RF', team_name, year),
                "SS": get_batting_position_info_WAR('SS', team_name, year),
                "2B": get_batting_position_info_WAR('2B', team_name, year),
                "3B": get_batting_position_info_WAR('3B', team_name, year),
                "C": get_batting_position_info_WAR('C', team_name, year),
                "1B": get_batting_position_info_WAR('1B', team_name, year)
            }
        elif stat_type == "wRC_plus":
            updated_data = {
                "LF": get_batting_position_info_wRC_plus('LF', team_name, year),
                "CF": get_batting_position_info_wRC_plus('CF', team_name, year),
                "RF": get_batting_position_info_wRC_plus('RF', team_name, year),
                "SS": get_batting_position_info_wRC_plus('SS', team_name, year),
                "2B": get_batting_position_info_wRC_plus('2B', team_name, year),
                "3B": get_batting_position_info_wRC_plus('3B', team_name, year),
                "C": get_batting_position_info_wRC_plus('C', team_name, year),
                "1B": get_batting_position_info_wRC_plus('1B', team_name, year)
            }
        elif stat_type == "wOBA":
            updated_data = {
                "LF": get_batting_position_info_wOBA('LF', team_name, year),
                "CF": get_batting_position_info_wOBA('CF', team_name, year),
                "RF": get_batting_position_info_wOBA('RF', team_name, year),
                "SS": get_batting_position_info_wOBA('SS', team_name, year),
                "2B": get_batting_position_info_wOBA('2B', team_name, year),
                "3B": get_batting_position_info_wOBA('3B', team_name, year),
                "C": get_batting_position_info_wOBA('C', team_name, year),
                "1B": get_batting_position_info_wOBA('1B', team_name, year)
            }
        else:
            return jsonify({"error": "Invalid stat type"}), 400
    elif category == "pitchers":
        if stat_type == "playing-time":
            updated_data = {
                "SP": get_pitching_position_info_playing_time('SP', team_name, year),
                "RP": get_pitching_position_info_playing_time('RP', team_name, year)
            }
        elif stat_type == "IP":
            updated_data = {
                "SP": get_pitching_position_info_IP('SP', team_name, year),
                "RP": get_pitching_position_info_IP('RP', team_name, year)
            }
        elif stat_type == "ERA":
            updated_data = {
                "SP": get_pitching_position_info_ERA('SP', team_name, year),
                "RP": get_pitching_position_info_ERA('RP', team_name, year)
            }
        elif stat_type == "FIP":
            updated_data = {
                "SP": get_pitching_position_info_FIP('SP', team_name, year),
                "RP": get_pitching_position_info_FIP('RP', team_name, year)
            }
        else:
            return jsonify({"error": "Invalid stat type"}), 400
    else:
            return jsonify({"error": "Invalid category"}), 400
    
    return jsonify(updated_data)