from flask import Blueprint, request, render_template
from sqlalchemy import func

from app.models import People, Batting, Teams, db, Fielding, Awards, HallOfFame, AllStarFull, Appearances

bp = Blueprint('search', __name__)


def get_players_team_team(option1_details, option2_details):
    """
    This function retrieves players who have played on both of the selected teams,
    ordered by the total number of stints on the two teams (least to most).

    :param option1_details: Name of the first team.
    :param option2_details: Name of the second team.
    :return: List of players who have played for both teams.
    """
    subquery = (
        db.session.query(
            Appearances.playerID,
            db.func.count(Teams.team_name.distinct()).label("team_count"),
            db.func.sum(Appearances.G_all).label("total_games")  # Using G_all for total games played
        )
        .join(Teams, Teams.teamID == Appearances.teamId)  # Join with Teams table based on teamId
        .filter(Teams.team_name.in_([option1_details, option2_details]))  # Filter by both teams
        .group_by(Appearances.playerID)  # Group by playerID to get distinct players
        .having(db.func.count(Teams.team_name.distinct()) == 2)  # Ensure player played for both teams
        .subquery()
    )

    results = (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(subquery, subquery.c.playerID == People.playerID)  # Join with the subquery on playerID
        .order_by(subquery.c.total_games)  # Order by total games played (ascending)
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
        "Rookie of the Year",
        "Most Valuable Player"
    ]
    if award in standard_awards:
        # Subquery to calculate the total games played (G_all) for each player for the specified team
        game_count = (
            db.session.query(Appearances.playerID, db.func.sum(Appearances.G_all).label("total_games"))
            .join(Teams, Teams.teamID == Appearances.teamId)  # Match Teams to Appearances
            .filter(Teams.team_name == team)  # Filter for the specified team name
            .group_by(Appearances.playerID)  # Group by playerID to calculate totals
            .subquery()  # Create a subquery so we can reference it in the main query
        )

        # Main query to get players sorted by least games played for the team who won the specified award
        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(game_count, game_count.c.playerID == People.playerID)  # Join with the game count subquery
            .join(Appearances, Appearances.playerID == People.playerID)  # Join to ensure the player appeared for the team
            .join(Teams, Teams.teamID == Appearances.teamId)  # Match Teams to filter by team
            .join(Awards, Awards.playerID == People.playerID)  # Join with Awards to match the award
            .filter(
                Teams.team_name == team,  # Ensure they played for the specified team
                Awards.awardID == award,  # Ensure the player won the specified award
                Awards.yearID == Appearances.yearID  # Match the award year with the appearance year
            )
            .order_by(game_count.c.total_games.asc())  # Order by the least games played
            .distinct()  # Ensure no duplicate rows
            .all()
        )
    elif award == "Hall of Fame":
        game_count = (
            db.session.query(Appearances.playerID, db.func.sum(Appearances.G_all).label("total_games"))
            .join(Teams, Teams.teamID == Appearances.teamId)
            .filter(Teams.team_name == team)  # Filter by the team name
            .group_by(Appearances.playerID)  # Group by player ID to calculate totals
            .subquery()
        )

        # Main query to retrieve Hall of Fame players, sorted by least games played for the team
        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(game_count, game_count.c.playerID == People.playerID)  # Link players to their game totals
            .join(Appearances, Appearances.playerID == People.playerID)  # Ensure they played for the team
            .join(Teams, Teams.teamID == Appearances.teamId)  # Join to filter by team
            .join(HallOfFame, HallOfFame.playerID == People.playerID)  # Check Hall of Fame status
            .filter(
                Teams.team_name == team,  # Match the specified team
                HallOfFame.inducted == "Y"  # Include only inducted players
            )
            .order_by(game_count.c.total_games.asc())  # Sort by the least games played
            .distinct()  # Avoid duplicate players
            .all()
        )
    elif award == "All Star":
        gp_count = (
            db.session.query(AllStarFull.playerID, db.func.sum(AllStarFull.GP).label("total_games"))
            .join(Teams, Teams.teamID == AllStarFull.teamID)
            .filter(Teams.team_name == team)
            .group_by(AllStarFull.playerID)
            .subquery()
        )

        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(gp_count, gp_count.c.playerID == People.playerID)  # Join with the games played subquery
            .order_by(gp_count.c.total_games.asc())  # Order by total games played, least games first
            .distinct()
            .all()
        )

    return results



def get_players_position_team(position, team):
    """
    This function retrieves players who played a specific position for a particular team,
    ordered by the number of appearances in that position (from least to most).
    It assumes the position is passed as a string like 'ss', '1b', etc.

    :param position: The position the player played (e.g., 'ss' for shortstop).
    :param team: The name of the team.
    :return: List of players who played the specified position for the given team, ordered by appearance count.
    """
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'

    results = (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamId)
        .filter(Teams.team_name == team, getattr(Appearances, position_column) > 0)  # Player appeared at least once in the position
        .group_by(People.playerID)  # Group by player to count their appearances
        .order_by(func.sum(getattr(Appearances, position_column)))  # Order by appearance count (least to most)
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