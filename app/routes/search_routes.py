from flask import Blueprint, request, render_template
from app.models import People, Batting, Teams, db

bp = Blueprint('search', __name__)

@bp.route('/search_players', methods=['POST'])
def search_players():
    option1 = request.form.get('option1')
    option1_details = request.form.get('dropdown1_details')
    option2 = request.form.get('option2')
    option2_details = request.form.get('dropdown2_details')

    if not option1 or not option2:
        return "Please select an option from both dropdowns.", 400

    results = []
    # Query logic here...
    if results:
        return render_template('results.html', results=results)
    return render_template('results.html', results=[], message="No matching results found.")
