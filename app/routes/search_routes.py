from flask import Blueprint, request, render_template
from app.models import People, Batting, Teams, db, Fielding, Awards, HallOfFame, AllStarFull

bp = Blueprint('search', __name__)


def get_players_team_team(option1_details, option2_details):
    """
    This function retrieves players who have played on both of the selected teams.

    :param option1_details: Name of the first team.
    :param option2_details: Name of the second team.
    :return: List of players who have played for both teams.
    """
    results = (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Teams, Teams.teamID == Batting.teamID)
        .filter(Teams.team_name.in_([option1_details, option2_details]))
        .group_by(People.playerID)
        .having(db.func.count(Teams.team_name.distinct()) == 2)
        .all()
    )
    return results


def get_players_award_team(award, team):
    """
    Query players who received a specific award and played for a specific team.
    Handles different logic based on the award type.
    """
    # Awards that use the current query logic
    standard_awards = [
        "Gold Glove",
        "Cy Young Award",
        "Silver Slugger",
        "Rookie of the Year Award",
        "Most Valuable Player"
    ]
    if award in standard_awards:
        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(Batting, Batting.playerID == People.playerID)
            .join(Teams, Teams.teamID == Batting.teamID)
            .join(Awards, Awards.playerID == People.playerID)
            .filter(Teams.team_name == team, Awards.awardID == award, Awards.yearID == Batting.yearID)
            .distinct()
            .all()
        )
    elif award == "Hall of Fame":
        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(Batting, Batting.playerID == People.playerID)  # Join Batting for player stats
            .join(Teams, Teams.teamID == Batting.teamID)  # Join Teams to filter by team
            .join(HallOfFame, HallOfFame.playerID == People.playerID)  # Join HallOfFame for inducted players
            .filter(Teams.team_name == team, HallOfFame.inducted == "Y")  # Filter by team and inducted status
            .distinct()
            .all()
        )
    elif award == "All Star":
        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(AllStarFull, AllStarFull.playerID == People.playerID)  # Join with AllStarFull table
            .join(Teams, Teams.teamID == AllStarFull.teamID)  # Join with Teams table
            .filter(Teams.team_name == team)  # Filter by the selected team
            .distinct()
            .all()
        )

    return results



def get_players_position_team(position, team):
    """
    This function retrieves players who played a specific position for a particular team.

    :param position: The position the player played (e.g., 'SS' for shortstop).
    :param team: The name of the team.
    :return: List of players who played the specified position for the given team.
    """
    results = (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Fielding, Fielding.playerID == People.playerID)
        .join(Teams, Teams.teamID == Fielding.teamID)
        .filter(Fielding.position == position, Teams.team_name == team, Fielding.f_G >= 1)  # Played at least 1 game
        .distinct()
        .all()
    )
    return results


@bp.route('/search_players', methods=['POST'])
def search_players():
    # Extract dropdown values
    option1 = request.form.get('option1')
    option1_details = request.form.get('dropdown1_details')
    option2 = request.form.get('option2')
    option2_details = request.form.get('dropdown2_details')

    # Validate input
    if not option1 or not option2:
        return "Please select an option from both dropdowns.", 400

    results = []

    # Handle search logic based on selected options
    if option1 == "teams" and option2 == "teams":
        # Query players who played on both selected teams
        results = get_players_team_team(option1_details, option2_details)

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
    elif (option1 == "awards" and option2 == "teams") or (option1 == "teams" and option2 == "awards"):
        # Extract the award and team details
        award = option1_details if option1 == "awards" else option2_details
        team = option1_details if option1 == "teams" else option2_details

        results = get_players_award_team(award, team)

    elif (option1 == "positions" and option2 == "teams") or (option1 == "teams" and option2 == "positions"):
        # Extract the position and team details
        position = option1_details if option1 == "positions" else option2_details
        team = option1_details if option1 == "teams" else option2_details

        results = get_players_position_team(position, team)

    elif (option1 == "teams" and option2 == "seasonal statistic") or (option1 == "seasonal statistic" and option2 == "teams"):
        if option1 == "teams":
            team = option1_details  # option1 holds the team details
            stat = option2_details  # option2 holds the stat details
        else:
            team = option2_details  # if option1 is not "teams", then option2 must be "teams"
            stat = option1_details  # if option2 is "teams", then option1 must be "seasonal statistic"

        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "teams" else request.form.get(
            f'dropdown1_{stat}_specific')
        stat_range = int(stat_range.replace('+', ''))


        if stat == "HR":
            # Query for Home Runs (HR) greater than or equal to the selected range
            results = (
                db.session.query(People.nameFirst, People.nameLast)
                .join(Batting, Batting.playerID == People.playerID)  # Join Batting for player stats
                .join(Teams, Teams.teamID == Batting.teamID)  # Join Teams to filter by team
                .filter(Teams.team_name == team, Batting.b_HR >= stat_range)  # Filter by the selected team
                .distinct()
                .all()
            )
        elif stat == "Win": #this needs fixed it isn't correct
            results = (
                db.session.query(People.nameFirst, People.nameLast)
                .join(Batting, Batting.playerID == People.playerID)
                .join(Teams, Teams.teamID == Batting.teamID)
                .filter(Teams.team_name == team, Teams.team_W >= stat_range)
                .distinct().all()
            )
        elif stat == "RBI":
            results = (
                db.session.query(People.nameFirst, People.nameLast)
                .join(Batting, Batting.playerID == People.playerID)  # Join Batting for player stats
                .join(Teams, Teams.teamID == Batting.teamID)  # Join Teams to filter by team
                .filter(Teams.team_name == team, Batting.b_RBI >= stat_range)  # Filter by the selected team
                .distinct()
                .all()
            )
        elif stat == "Run":
            results = (
                db.session.query(People.nameFirst, People.nameLast)
                .join(Batting, Batting.playerID == People.playerID)  # Join Batting for player stats
                .join(Teams, Teams.teamID == Batting.teamID)  # Join Teams to filter by team
                .filter(Teams.team_name == team, Batting.b_R >= stat_range)  # Filter by the selected team
                .distinct()
                .all()
            )
        elif stat == "Hits":
            results = (
                db.session.query(People.nameFirst, People.nameLast)
                .join(Batting, Batting.playerID == People.playerID)  # Join Batting for player stats
                .join(Teams, Teams.teamID == Batting.teamID)  # Join Teams to filter by team
                .filter(Teams.team_name == team, Batting.b_H >= stat_range)  # Filter by the selected team
                .distinct()
                .all()
            )
        elif stat == "SB":
            results = (
                db.session.query(People.nameFirst, People.nameLast)
                .join(Batting, Batting.playerID == People.playerID)  # Join Batting for player stats
                .join(Teams, Teams.teamID == Batting.teamID)  # Join Teams to filter by team
                .filter(Teams.team_name == team, Batting.b_SB >= stat_range)  # Filter by the selected team
                .distinct()
                .all()
            )





    else:
        return "Invalid selection or combination. Please try again.", 400
        # Render results
        # Render results

    if results:
        return render_template('results.html', results=results)
    else:
        return render_template(
            'results.html',
            results=[],
            message="No matching results found for your query."
        )