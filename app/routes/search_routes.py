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
    
    # Handle search logic based on selected options
    if option1 == "teams" and option2 == "teams":
        # Query players who played on both selected teams
        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(Batting, Batting.playerID == People.playerID)
            .join(Teams, Teams.teamID == Batting.teamID)
            .filter(Teams.team_name.in_([option1_details, option2_details]))
            .group_by(People.playerID, People.nameFirst, People.nameLast)
            .having(db.func.count(Teams.team_name.distinct()) == 2)
            .all()
        )
    elif (option1 == "career statistics" and option2 == "teams") or (option2 == "career statistics" and option1 == "career statistics"):

        # Example: Query career statistics
        # You may need to refine this based on the exact statistics you want to display
        if option1 == "career statistics":
            stat = option1_details
        else:
            stat = option2_details

        # Mock query: Replace this with actual stat-based query logic
        results = (
            db.session.query(People.nameFirst, People.nameLast, Batting.stat_column)
            .filter(Batting.stat_column >= stat)  # Replace `stat_column` with actual stat field
            .all()
        )
    else:
        return "Invalid selection or combination. Please try again.", 400
        # Render results
        # Render results
    
    if results:
        return render_template('results.html', results=results)
    return render_template('results.html', results=[], message="No matching results found.")
