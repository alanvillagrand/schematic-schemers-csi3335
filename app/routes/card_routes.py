from flask import Blueprint, render_template, session, redirect, url_for
from app.services import cardQueries

bp = Blueprint('card', __name__)

@bp.route("/card")
def card():
    return render_template("card.html")

@bp.route("/card/create")
def card_create():
    results = cardQueries.get_player_card_info("Babe Ruth")
    if results:
        return render_template("card_creator.html", results=results)
    return url_for("card.card")