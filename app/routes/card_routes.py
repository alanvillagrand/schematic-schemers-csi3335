from flask import Blueprint, render_template, session, redirect, url_for, request
from app.services import cardQueries

bp = Blueprint('card', __name__)


@bp.route('/card', methods=['GET', 'POST'])
def card():
    if "username" in session:
        if request.method == 'POST':
            player_name = request.form['player']
            results = cardQueries.get_player_card_info(player_name)
            return render_template("card_creator.html", results=results)
        return render_template("card.html")
    return redirect(url_for('main.home'))

@bp.route("/card/create")
def card_create():
    results = cardQueries.get_player_card_info("Babe Ruth")
    if results:
        return render_template("card_creator.html", results=results)
    return url_for("card.card")