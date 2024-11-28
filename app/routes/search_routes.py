from flask import Blueprint, request, render_template
from sqlalchemy import func

from app.models import People, Batting, Teams, db, Fielding, Awards, HallOfFame, AllStarFull, Appearances, Pitching, \
    SeriesPost, FieldingPost, BattingPost

bp = Blueprint('search', __name__)

""" 
get_players_team_team
Queries a player that played for two different teams
Takes in the two teams as parameters
Algorithm uses the appearances table to get players with the least total appearances
"""
def get_players_team_team(option1_details, option2_details):

    subquery = (
        db.session.query(
            Appearances.playerID,
            db.func.count(Teams.team_name.distinct()).label("team_count"),
            db.func.sum(Appearances.G_all).label("total_games")
        )
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(Teams.team_name.in_([option1_details, option2_details]))
        .group_by(Appearances.playerID)
        .having(db.func.count(Teams.team_name.distinct()) == 2)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(subquery, subquery.c.playerID == People.playerID)
        .order_by(subquery.c.total_games)
        .all()
    )


""" 
get_players_stdAward_team
Queries a player that won a standard award and played for a particular team (must have won the standard award in
a season he appeared for that team)
Takes in a standard award and a team
Algorithm uses the appearances table to get players with the least total appearances
"""
def get_players_stdAward_team(stdAward, team):
    game_count = (
            db.session.query(Appearances.playerID, db.func.sum(Appearances.G_all).label("total_games"))
            .join(Teams, Teams.teamID == Appearances.teamID)
            .filter(Teams.team_name == team)
            .group_by(Appearances.playerID)
            .subquery()
        )

    return (
            db.session.query(People.nameFirst, People.nameLast)
            .join(game_count, game_count.c.playerID == People.playerID)
            .join(Appearances, Appearances.playerID == People.playerID)
            .join(Teams, Teams.teamID == Appearances.teamID)
            .join(Awards, Awards.playerID == People.playerID)
            .filter(
                Teams.team_name == team,
                Awards.awardID == stdAward,
                Awards.yearID == Appearances.yearID
            )
            .order_by(game_count.c.total_games.asc())
            .distinct()
            .all()
        )


""" 
get_players_hof_team
Queries a player that is in the hall of fame and played for a particular team (When paired with a team,
the player must have played a major league game for the team in question)
Takes in a team
Algorithm uses the appearances table to get players with the least total appearances
"""
def get_players_hof_team(team):
    game_count = (
        db.session.query(Appearances.playerID, db.func.sum(Appearances.G_all).label("total_games"))
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(Teams.team_name == team)
        .group_by(Appearances.playerID)
        .subquery()
        )

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(game_count, game_count.c.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .filter(
            Teams.team_name == team,
            HallOfFame.inducted == "Y"
        )
        .order_by(game_count.c.total_games.asc())
        .distinct()
        .all()
    )


""" 
get_players_allstar_team
Queries a player that played on the all star team and played for a particular team (When paired with a team,
the player must have represented that team in the All-Star Game)
Takes in a team
Algorithm uses the all star table to get players with the least total appearances
"""
def get_players_allstar_team(team):
        gp_count = (
            db.session.query(AllStarFull.playerID, db.func.sum(AllStarFull.GP).label("total_games"))
            .join(Teams, Teams.teamID == AllStarFull.teamID)
            .filter(Teams.team_name == team)
            .group_by(AllStarFull.playerID)
            .subquery()
        )

        return (
            db.session.query(People.nameFirst, People.nameLast)
            .join(gp_count, gp_count.c.playerID == People.playerID)
            .order_by(gp_count.c.total_games.asc())
            .distinct()
            .all()
        )

"""
get_players_position_team
Queries a player that played a particular position and played for a particular team
Takes in a position and a team
Algorithm uses the appearances table to get players with the least total appearances
"""
def get_players_position_team(position, team):

    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(Teams.team_name == team, getattr(Appearances, position_column) > 0, Appearances.teamID == Teams.teamID)  # Player appeared at least once in the position
        .group_by(People.playerID)  # Group by player to count their appearances
        .order_by(func.sum(getattr(Appearances, position_column)))  # Order by appearance count (least to most)
        .distinct()
        .all()
    )

"""
get_players_ws_team
Queries a player that played on the world series and played for a particular team
(When paired with a team, must have appeared in a postseason game
(or be on the World Series roster) for the team during the World Series-winning season.)
Takes in a team
Algorithm uses the appearances table to get players with the least total appearances
"""
def get_players_ws_team(team):
    game_count = (
        db.session.query(Appearances.playerID, db.func.sum(Appearances.G_all).label("total_games"))
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(Teams.team_name == team)
        .group_by(Appearances.playerID)
        .subquery()
    )

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(game_count, game_count.c.playerID == People.playerID)
        .join(FieldingPost, FieldingPost.playerID == People.playerID)
        .join(SeriesPost, SeriesPost.teamIDwinner == FieldingPost.teamID)
        .join(Teams, Teams.teamID == SeriesPost.teamIDwinner)
        .filter(Teams.team_name == team, SeriesPost.round == "WS", SeriesPost.yearID == FieldingPost.yearID)
        .order_by(game_count.c.total_games.asc())
        .distinct()
        .all()
    )


"""
get_players_seasonStatBatting_team
Queries a player that achieved that batting stat while playing on a team in a single season.
Takes in a team, the stat_column, and the stat range
Algorithm uses the batting table to get players with the least total appearances (b_G)
"""
def get_players_seasonStatBatting_team(stat_column, team, stat_range):

    batting_column = getattr(Batting, f"b_{stat_column}")
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)  # Join Batting for player stats
        .join(Teams, Teams.teamID == Batting.teamID)  # Join Teams to filter by team
        .filter(Teams.team_name == team, batting_column >= stat_range)  # Filter by team and stat range
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )




"""
get_players_stdAward_position
get players that won a standard award and played for a particular position
(does not need to be in the same season)
takes in a award and position as parameters
Algorithm orders it by least number of times they played that position
"""
def get_players_stdAward_position(award, position):
    position_column = f'G_{position.lower()}'

    return (
            db.session.query(People.nameFirst, People.nameLast)
            .join(Appearances, Appearances.playerID == People.playerID)  # Join to check position
            .join(Awards, Awards.playerID == People.playerID)  # Join to check award
            .filter(
                getattr(Appearances, position_column) > 0,  # Played the specified position
                Awards.awardID == award  # Won the specified award
            )
            .group_by(People.playerID)  # Group by player ID
            .order_by(db.func.sum(getattr(Appearances, position_column)).asc())  # Order by least position appearances
            .distinct()
            .all()
        )



"""
get_players_hof_position
get players that are in the hall of fame and played for a particular position
(does not need to be in the same season)
takes in a position as parameters
Algorithm orders it by least number of times they played that position
"""
def get_players_hof_position(position):
    position_column = f'G_{position.lower()}'
    return (
            db.session.query(People.nameFirst, People.nameLast)
            .join(Appearances, Appearances.playerID == People.playerID)  # Join to check position
            .join(HallOfFame, HallOfFame.playerID == People.playerID)  # Check Hall of Fame status
            .filter(
                getattr(Appearances, position_column) > 0,  # Played the specified position
                HallOfFame.inducted == "Y"  # Inducted into the Hall of Fame
            )
            .group_by(People.playerID)
            .order_by(db.func.sum(getattr(Appearances, position_column)).asc())
            .distinct()
            .all()
        )


"""
get_players_allstar_position
get players that played in a all star game and played for a particular position
(does not need to be in the same season)
takes in a position as parameters
Algorithm orders it by least number of times they played that position
"""
def get_players_allstar_position(position):
    position_column = f'G_{position.lower()}'
    return (
            db.session.query(People.nameFirst, People.nameLast)
            .join(Appearances, Appearances.playerID == People.playerID)  # Join to check position
            .join(AllStarFull, AllStarFull.playerID == People.playerID)  # Check All-Star appearances
            .filter(
                getattr(Appearances, position_column) > 0,  # Played the specified position
                AllStarFull.GP > 0  # Appeared in an All-Star game
            )
            .group_by(People.playerID)
            .order_by(db.func.sum(getattr(Appearances, position_column)).asc())
            .distinct()
            .all()
        )




def get_players_stdAward_stdAward(award1, award2):
    # Subquery to find players who won the specified awards
    awards_query = (
        db.session.query(Awards.playerID)
        .filter(Awards.awardID.in_([award1, award2]))
        .group_by(Awards.playerID)
        .having(func.count(func.distinct(Awards.awardID)) == 2)
        .subquery()
    )

    # Main query to join with the People and Appearances tables, ordering by total appearances
    results = (
        db.session.query(People.nameFirst, People.nameLast)
        .join(awards_query, awards_query.c.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .group_by(People.playerID, People.nameFirst, People.nameLast)  # Group by player to get the sum of appearances
        .having(func.sum(Appearances.G_all).isnot(None))  # Ensure that the player has appearances
        .order_by(func.sum(Appearances.G_all).asc())  # Order by total appearances in ascending order
        .all()
    )

    return results


def get_players_pob_position(position):
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'

    results = (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(
            People.birthCountry != 'USA', getattr(Appearances, position_column) > 0 )
        .group_by(People.playerID)  # Group by player ID to calculate total appearances
        .order_by(func.sum(getattr(Appearances, position_column)))
        .distinct()
        .all()
    )
    return results



"""
get_players_seasonStatBatting_ws
queries for a player that is in the world series winning roster and 
has this season batting stat. does not need to be in the same season as the world series
takes in a stat_column, and stat_range
algorithm orders it by least appearances in batting b_G
"""
def get_players_seasonStatBatting_ws(stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(SeriesPost, SeriesPost.teamIDwinner == Batting.teamID)
        .filter(SeriesPost.round == "WS", SeriesPost.teamIDwinner == Batting.teamID, batting_column >= stat_range)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()

    )

"""
get_players_seasonBattingAVG_ws
queries for a player that has this average stat and achieved it in a season
while playing for the specific team
takes in a team and stat_range
algorithm orders it by least appearances in batting b_G
"""
def get_players_seasonBattingAVG_team(stat_range, team):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Teams, Teams.teamID == Batting.teamID)
        .filter((Batting.b_H/ Batting.b_AB) >= stat_range)  # Batting average of .300 or higher
        .filter(Teams.team_name == team)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonBatting3030_team(team):
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Teams, Teams.teamID == Batting.teamID)
        .filter(Teams.team_name == team)
        .filter(Batting.b_SB > 30)
        .filter(Batting.b_HR > 30)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )





"""
get_players_seasonStatBatting_stdAward
queries for a player that has this batting stat and won this standard award. Does not have to be in the same season.
takes in a award and stat_range, and stat_column
algorithm orders it by least appearances in batting b_G
"""
def get_players_seasonStatBatting_stdAward(stat_column, award, stat_range):

    batting_column = getattr(Batting, f"b_{stat_column}")
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)  # Join to check stat
        .join(Awards, Awards.playerID == People.playerID)  # Join to check awards
        .filter(
            batting_column >= stat_range,  # Check if the player achieved the minimum stat threshold
            Awards.awardID == award  # Check if the player won the specified award
        )
        .group_by(People.playerID)  # Group by player to ensure distinct results
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )


def get_players_seasonStatBatting_position(stat_column, position, stat_range):
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'
    batting_column = getattr(Batting, f"b_{stat_column}")

    results = (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(
            batting_column >= stat_range, getattr(Appearances, position_column) > 0 )
        .group_by(People.playerID)  # Group by player ID to calculate total appearances
        .order_by(func.sum(getattr(Appearances, position_column)))
        .distinct()
        .all()
    )
    return results

"""
get_players_seasonStatPitching_team
queries for a player that has this pitching stat and achieved it in a season
takes in a team, stat, and stat_range
algorithm orders it by least appearances in pitching p_G
"""

def get_players_seasonStatPitching_team(stat_column, team, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Teams, Teams.teamID == Pitching.teamID)
        .filter(pitching_column >= stat_range)
        .filter(Teams.team_name == team)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()


    )


def get_players_careerBattingAVG_team(team, min_avg=0.300):
    batting_avg = (db.func.sum(Batting.b_H) / db.func.nullif(db.func.sum(Batting.b_AB), 0)).label("career_avg")

    results = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            batting_avg
        )
        .join(Batting, Batting.playerID == People.playerID)
        .join(Teams, Teams.teamID == Batting.teamID)
        .filter(Teams.team_name == team)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having(batting_avg >= min_avg)
        .order_by(batting_avg.desc())
        .all()
    )

    return results


def get_players_career_batting_stat_team(team, stat_column, min_value=None, max_value=None):
    """
    Get players' career batting statistics for a given team.

    :param team: Team name to filter players by
    :param stat_column: The batting statistic column to aggregate (e.g., 'b_H', 'b_HR', 'b_WAR')
    :param min_value: Minimum value for filtering (e.g., 2000 for hits)
    :param max_value: Maximum value for filtering
    :return: List of players with their aggregated statistics
    """
    stat_sum = db.func.sum(getattr(Batting, stat_column)).label("career_stat")

    query = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            stat_sum
        )
        .join(Batting, Batting.playerID == People.playerID)
        .join(Teams, Teams.teamID == Batting.teamID)
        .filter(Teams.team_name == team)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
    )

    if min_value is not None:
        query = query.having(stat_sum >= min_value)
    if max_value is not None:
        query = query.having(stat_sum <= max_value)

    results = query.order_by(stat_sum.desc()).all()

    return results

"""
get_players_seasonStatPitching_seasonStatPitching
queries for a player that has these 2 pitching stats. doesn't have to be in the same season
takes in a both stats and their ranges
algorithm orders it by least appearances in pitching p_G
"""
def get_players_seasonStatPitching_seasonStatPitching(stat_column1, stat_range1, stat_column2, stat_range2):
    pitching_column1 = getattr(Pitching, f"p_{stat_column1}")
    pitching_column2 = getattr(Pitching, f"p_{stat_column2}")

    # Subqueries to check for each stat independently
    stat1_subquery = (
        db.session.query(Pitching.playerID)
        .filter(pitching_column1 >= stat_range1)
        .subquery()
    )
    stat2_subquery = (
        db.session.query(Pitching.playerID)
        .filter(pitching_column2 >= stat_range2)
        .subquery()
    )

    # Main query: find players present in both subqueries
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(stat1_subquery, stat1_subquery.c.playerID == People.playerID)
        .join(stat2_subquery, stat2_subquery.c.playerID == People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .group_by(People.playerID)
        .distinct()
        .all()
    )

def get_players_career_pitching_stat_team(team, stat_column, min_value=None, max_value=None):
    """
    Get players' career statistics for a given team.

    :param team: Team name to filter players by
    :param stat_column: The pitching statistic column to aggregate (e.g., 'p_W', 'p_SO', 'p_SV')
    :param min_value: Minimum value for filtering (e.g., 200 for wins)
    :param max_value: Maximum value for filtering (e.g., 3.00 for ERA)
    :return: List of players with their aggregated statistics
    """
    # Use dynamic attribute access to reference the correct column
    stat_sum = db.func.sum(getattr(Pitching, stat_column)).label("career_stat")

    # Base query
    query = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            stat_sum
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Teams, Teams.teamID == Pitching.teamID)
        .filter(Teams.team_name == team)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
    )

    # Add bounds if provided
    if min_value is not None:
        query = query.having(stat_sum >= min_value)
    if max_value is not None:
        query = query.having(stat_sum <= max_value)

    # Order by the statistic descending
    results = query.order_by(stat_sum.desc()).all()

    return results


"""
currently not working too hard :/
"""
def get_players_career_war_team(team, min_war=40):
    return (
        # db.session.query(
        #     People.nameFirst,
        #     People.nameLast,
        #     (db.func.sum(Batting.b_WAR) + db.func.sum(Pitching.p_WAR)).label("career_war")
        # )
        # .join(Batting, Batting.playerID == People.playerID)
        # .join(Pitching, Pitching.playerID == People.playerID, isouter=True)
        # .join(Teams, Teams.teamID == Batting.teamID)
        # .filter(Teams.team_name == team)
        # .group_by(People.playerID)
        # .having(db.func.sum(Batting.b_WAR) + db.func.sum(Pitching.p_WAR) >= min_war)
        # .order_by((db.func.sum(Batting.b_WAR) + db.func.sum(Pitching.p_WAR)).desc())
        # .all()
    )


def get_players_career_era_team(team, max_era=3.00):
    # Calculate the sum of ERA and count to get the average ERA
    sum_era = db.func.sum(Pitching.p_ERA).label("sum_era")
    count_era = db.func.count(Pitching.p_ERA).label("count_era")
    avg_era = (sum_era / db.func.nullif(count_era, 0)).label("career_avg_era")

    results = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            avg_era
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Teams, Teams.teamID == Pitching.teamID)
        .filter(pitching_column >= stat_range)
        .filter(Teams.team_name == team)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(avg_era <= max_era)  # Only include players with avg ERA under 3.00
        .order_by(avg_era.asc())
        .all()
    )

    return results


"""
queries for career stats and awards
WAR and ERA NOT DONE
"""


def get_players_careerBattingAVG_award(award, min_avg=0.300):
    batting_avg = (db.func.sum(Batting.b_H) / db.func.nullif(db.func.sum(Batting.b_AB), 0)).label("career_avg")

    results = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            batting_avg
        )
        .join(Batting, Batting.playerID == People.playerID)
        .join(Teams, Teams.teamID == Batting.teamID)
        .filter(Awards.awardID == award)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having(batting_avg >= min_avg)
        .order_by(batting_avg.desc())
        .all()
    )

    return results

def get_players_seasonStatPitching_stdAward(award, stat_column, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(pitching_column >= stat_range)
        .filter(Awards.awardID == award)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()

    )

"""
get_players_seasonStatPitching_seasonStatBatting
queries for a player that has this pitching stat and this batting stat.
doesn't have to be in the same season
algorithm orders it by least appearances in pitching p_G
"""
def get_players_seasonStatPitching_seasonStatBatting(pitching_column, pitching_range, batting_column, batting_range):
    pitching_column1 = getattr(Pitching, f"p_{pitching_column}")
    batting_column1 = getattr(Batting, f"b_{batting_column}")

    # Subqueries to check for each stat independently
    pitching_subquery = (
        db.session.query(Pitching.playerID)
        .filter(pitching_column1 >= pitching_range)
        .subquery()
    )
    batting_subquery = (
        db.session.query(Batting.playerID)
        .filter(batting_column1 >= batting_range)
        .subquery()
    )

    # Main query: find players present in both subqueries
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(pitching_subquery, pitching_subquery.c.playerID == People.playerID)
        .join(batting_subquery, batting_subquery.c.playerID == People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .group_by(People.playerID)
        .distinct()
        .all()
    )
def get_players_career_batting_stat_award(award, stat_column, min_value=None, max_value=None):
    """
    Queries players' career batting statistics and awards.

    :param stat_column: The career batting statistic column to aggregate (e.g., 'b_H', 'b_HR')
    :param award: The award the player must have won (e.g., 'Gold Glove', 'Most Valuable Player')
    :param min_value: Minimum value for filtering the statistic
    :param max_value: Maximum value for filtering the statistic
    :return: List of players with their aggregated statistics who have won the specified award
    """
    # Calculate the career statistic
    stat_sum = db.func.sum(getattr(Batting, stat_column)).label("career_stat")

    # Base query to get players with their career stats
    query = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            stat_sum
        )
        .join(Batting, Batting.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(
            Awards.awardID == award
        )
        .group_by(People.playerID, People.nameFirst, People.nameLast)
    )

    # Add bounds if provided
    if min_value is not None:
        query = query.having(stat_sum >= min_value)
    if max_value is not None:
        query = query.having(stat_sum <= max_value)

    # Order by the statistic descending
    results = query.order_by(stat_sum.desc()).distinct().all()

    return results


def get_players_career_pitching_stat_award(award, stat_column, min_value=None, max_value=None):
    """
    Queries players' career pitching statistics and awards.

    :param stat_column: The career pitching statistic column to aggregate (e.g., 'p_W', 'p_SO')
    :param award: The award the player must have won (e.g., 'Cy Young Award', 'Most Valuable Player')
    :param min_value: Minimum value for filtering the statistic
    :param max_value: Maximum value for filtering the statistic
    :return: List of players with their aggregated statistics who have won the specified award
    """
    # Calculate the career statistic
    stat_sum = db.func.sum(getattr(Pitching, stat_column)).label("career_stat")

    # Base query to get players with their career stats
    query = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            stat_sum
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(
            Awards.awardID == award
        )
        .group_by(People.playerID, People.nameFirst, People.nameLast)
    )

    # Add bounds if provided
    if min_value is not None:
        query = query.having(stat_sum >= min_value)
    if max_value is not None:
        query = query.having(stat_sum <= max_value)

    # Order by the statistic descending
    results = query.order_by(stat_sum.desc()).distinct().all()

    return results


"""
currently not working too hard :/
"""
def get_players_career_war_award(award, min_war=40):
    return (
        # db.session.query(
        #     People.nameFirst,
        #     People.nameLast,
        #     (db.func.sum(Batting.b_WAR) + db.func.sum(Pitching.p_WAR)).label("career_war")
        # )
        # .join(Batting, Batting.playerID == People.playerID)
        # .join(Pitching, Pitching.playerID == People.playerID, isouter=True)
        # .join(Teams, Teams.teamID == Batting.teamID)
        # .filter(Teams.team_name == team)
        # .group_by(People.playerID)
        # .having(db.func.sum(Batting.b_WAR) + db.func.sum(Pitching.p_WAR) >= min_war)
        # .order_by((db.func.sum(Batting.b_WAR) + db.func.sum(Pitching.p_WAR)).desc())
        # .all()
    )


def get_players_career_era_award(award, max_era=3.00):
    # Calculate the sum of ERA and count to get the average ERA
    sum_era = db.func.sum(Pitching.p_ERA).label("sum_era")
    count_era = db.func.count(Pitching.p_ERA).label("count_era")
    avg_era = (sum_era / db.func.nullif(count_era, 0)).label("career_avg_era")

    results = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            avg_era
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(Awards.awardID == award)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(avg_era <= max_era)  # Only include players with avg ERA under 3.00
        .order_by(avg_era.asc())
        .all()
    )

    return results


"""
queries for positions and career stats
"""


def get_players_career_batting_stat_position(position, stat_column, min_value=None, max_value=None):
    """
    Get players' career batting statistics for a given position.

    :param position: Position to filter players by
    :param stat_column: The batting statistic column to aggregate (e.g., 'b_H', 'b_HR', 'b_WAR')
    :param min_value: Minimum value for filtering (e.g., 2000 for hits)
    :param max_value: Maximum value for filtering
    :return: List of players with their aggregated statistics
    """
    stat_sum = db.func.sum(getattr(Batting, stat_column)).label("career_stat")

    query = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            stat_sum
        )
        .join(Batting, Batting.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(Appearances.POS == position)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
    )

    if min_value is not None:
        query = query.having(stat_sum >= min_value)
    if max_value is not None:
        query = query.having(stat_sum <= max_value)

    results = query.order_by(stat_sum.desc()).all()

    return results


def get_players_career_pitching_stat_position(position, stat_column, min_value=None, max_value=None):
    """
    Get players' career pitching statistics for a given position.

    :param position: Position to filter players by
    :param stat_column: The pitching statistic column to aggregate (e.g., 'p_W', 'p_SO', 'p_SV')
    :param min_value: Minimum value for filtering (e.g., 200 for wins)
    :param max_value: Maximum value for filtering (e.g., 3.00 for ERA)
    :return: List of players with their aggregated statistics
    """
    # Use dynamic attribute access to reference the correct column
    stat_sum = db.func.sum(getattr(Pitching, stat_column)).label("career_stat")

    # Base query
    query = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            stat_sum
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(Appearances.POS == position)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
    )

    # Add bounds if provided
    if min_value is not None:
        query = query.having(stat_sum >= min_value)
    if max_value is not None:
        query = query.having(stat_sum <= max_value)

    # Order by the statistic descending
    results = query.order_by(stat_sum.desc()).all()

    return results


def get_players_career_era_position(position, max_era=3.00):
    """
    Get players' career ERA for a given position.

    :param position: Position to filter players by
    :param max_era: Maximum ERA value for filtering (e.g., 3.00)
    :return: List of players with their average ERA who played at the given position
    """
    # Calculate the sum of ERA and count to get the average ERA
    sum_era = db.func.sum(Pitching.p_ERA).label("sum_era")
    count_era = db.func.count(Pitching.p_ERA).label("count_era")
    avg_era = (sum_era / db.func.nullif(count_era, 0)).label("career_avg_era")

    results = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            avg_era
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(Appearances.POS == position)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(avg_era <= max_era)  # Only include players with avg ERA under max_era
        .order_by(avg_era.asc())
        .all()
    )



def get_players_careerBattingAVG_position(position, min_avg=0.300):
    batting_avg = (db.func.sum(Batting.b_H) / db.func.nullif(db.func.sum(Batting.b_AB), 0)).label("career_avg")


    results = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            batting_avg
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(Appearances.POS == position)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having(batting_avg >= min_avg)
        .order_by(batting_avg.desc())
        .all()
    )

    return results


def get_players_career_war_position():
    return


"""
queries for POB and career stats
"""


def get_players_career_batting_stat_pob(stat_column, min_value=None, max_value=None):
    """
    Get players' career batting statistics for those born outside the USA.

    :param stat_column: The batting statistic column to aggregate (e.g., 'b_H', 'b_HR', 'b_WAR')
    :param min_value: Minimum value for filtering (e.g., 2000 for hits)
    :param max_value: Maximum value for filtering
    :return: List of players with their aggregated statistics
    """
    stat_sum = db.func.sum(getattr(Batting, stat_column)).label("career_stat")

    query = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            stat_sum
        )
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.birthCountry != 'USA')
        .group_by(People.playerID, People.nameFirst, People.nameLast)
    )

    if min_value is not None:
        query = query.having(stat_sum >= min_value)
    if max_value is not None:
        query = query.having(stat_sum <= max_value)

    results = query.order_by(stat_sum.desc()).all()

    return results


def get_players_career_pitching_stat_pob(stat_column, min_value=None, max_value=None):
    """
    Get players' career pitching statistics for those born outside the USA.

    :param stat_column: The pitching statistic column to aggregate (e.g., 'p_W', 'p_SO', 'p_SV')
    :param min_value: Minimum value for filtering (e.g., 200 for wins)
    :param max_value: Maximum value for filtering (e.g., 3.00 for ERA)
    :return: List of players with their aggregated statistics
    """
    stat_sum = db.func.sum(getattr(Pitching, stat_column)).label("career_stat")

    query = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            stat_sum
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(People.birthCountry != 'USA')
        .group_by(People.playerID, People.nameFirst, People.nameLast)
    )

    if min_value is not None:
        query = query.having(stat_sum >= min_value)
    if max_value is not None:
        query = query.having(stat_sum <= max_value)

    results = query.order_by(stat_sum.desc()).all()

    return results


def get_players_career_era_pob(max_era=3.00):
    """
    Get players' career ERA for those born outside the USA.

    :param max_era: Maximum ERA value for filtering (e.g., 3.00)
    :return: List of players with their average ERA who were born outside the USA
    """
    sum_era = db.func.sum(Pitching.p_ERA).label("sum_era")
    count_era = db.func.count(Pitching.p_ERA).label("count_era")
    avg_era = (sum_era / db.func.nullif(count_era, 0)).label("career_avg_era")

    results = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            avg_era
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(People.birthCountry != 'USA')
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(avg_era <= max_era)
        .order_by(avg_era.asc())
        .all()
    )

    return results


def get_players_careerBattingAVG_pob(min_avg=0.300):
    """
    Get players' career batting average for those born outside the USA.

    :param min_avg: Minimum batting average value for filtering (e.g., 0.300)
    :return: List of players with their batting average who were born outside the USA
    """
    batting_avg = (db.func.sum(Batting.b_H) / db.func.nullif(db.func.sum(Batting.b_AB), 0)).label("career_avg")

    results = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            batting_avg
        )
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.birthCountry != 'USA')
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having(batting_avg >= min_avg)
        .order_by(batting_avg.desc())
        .all()
    )

    return results


def get_players_career_war_pob(min_era=3.00):
    return


"""
queries for seasonal stats and career stats
"""


@bp.route('/search_players', methods=['POST'])
def search_players():
    standard_seasonStatBatting = [
        "HR",
        "RBI",
        "R",
        "H",
        "SB"
    ]
    standard_seasonStatPitching = [
        "SV",
        "W",
        "SO"
    ]
    # Extract dropdown values
    option1 = request.form.get('option1')
    option1_details = request.form.get('dropdown1_details')
    option2 = request.form.get('option2')
    option2_details = request.form.get('dropdown2_details')

    # Validate input
    if not option1 or not option2:
        return "Please select an option from both dropdowns.", 400

    results = []

    if option1 == "teams" and option2 == "teams":
        # Query players who played on both selected teams
        results = get_players_team_team(option1_details, option2_details)

    elif (option1 == "positions" and option2 == "teams") or (option1 == "teams" and option2 == "positions"):
        # Extract the position and team details
        position = option1_details if option1 == "positions" else option2_details
        team = option1_details if option1 == "teams" else option2_details
        results = get_players_position_team(position, team)

    elif (option1 == "career statistic" and option2 == "teams") or (option1 == "teams" and option2 == "career statistic"):
        print("IN TEAMS CSTATS")
        # Extract career statistics and team details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        team = option2_details if option1 == "career statistic" else option1_details

        # Handling different career statistics based on user input
        if career_stat == "300+ AVG Career Batting":
            results = get_players_careerBattingAVG_team(team, 0.300)
        elif career_stat == "200+ Wins Career Pitching":
            results = get_players_career_pitching_stat_team(team, stat_column="p_W", min_value=200)
        elif career_stat == "2000+ K Career Pitching":
            results = get_players_career_pitching_stat_team(team, stat_column="p_SO", min_value=2000)
        elif career_stat == "2000+ Hits Career Batting":
            results = get_players_career_batting_stat_team(team, stat_column="b_H", min_value=2000)
        elif career_stat == "300+ HR Career Batting":
            results = get_players_career_batting_stat_team(team, stat_column="b_HR", min_value=300)
        elif career_stat == "300+ Saves Career Pitching":
            results = get_players_career_pitching_stat_team(team, stat_column="p_SV", min_value=300)
        elif career_stat == "300+ Wins Career Pitching":
            results = get_players_career_pitching_stat_team(team, stat_column="p_W", min_value=300)
        elif career_stat == "3000+ K Career Pitching":
            results = get_players_career_pitching_stat_team(team, stat_column="p_SO", min_value=3000)
        elif career_stat == "3000+ Hits Career Batting":
            results = get_players_career_batting_stat_team(team, stat_column="b_H", min_value=3000)
        elif career_stat == "40+ WAR Career (calculated)":
            results = get_players_career_war_team(team, 40)
        elif career_stat == "≤ 3.00 ERA Career Pitching (calculated)":
            results = get_players_career_era_team(team, 3.00)

    elif (option1 == "career statistic" and option2 == "awards") or (option1 == "awards" and option2 == "career statistic"):
        print("IN AWARDS CSTATS")
        # Extract the award and career statistic details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        award = option2_details if option1 == "career statistic" else option1_details

        # Handling different career statistics based on user input
        if career_stat == "300+ AVG Career Batting":
            results = get_players_careerBattingAVG_award(award, 0.300)
        elif career_stat == "200+ Wins Career Pitching":
            results = get_players_career_pitching_stat_award(award, stat_column="p_W", min_value=200)
        elif career_stat == "2000+ K Career Pitching":
            results = get_players_career_pitching_stat_award(award, stat_column="p_SO", min_value=2000)
        elif career_stat == "2000+ Hits Career Batting":
            results = get_players_career_batting_stat_award(award, stat_column="b_H", min_value=2000)
        elif career_stat == "300+ HR Career Batting":
            results = get_players_career_batting_stat_award(award, stat_column="b_HR", min_value=300)
        elif career_stat == "300+ Saves Career Pitching":
            results = get_players_career_pitching_stat_award(award, stat_column="p_SV", min_value=300)
        elif career_stat == "300+ Wins Career Pitching":
            results = get_players_career_pitching_stat_award(award, stat_column="p_W", min_value=300)
        elif career_stat == "3000+ K Career Pitching":
            results = get_players_career_pitching_stat_award(award, stat_column="p_SO", min_value=3000)
        elif career_stat == "3000+ Hits Career Batting":
            results = get_players_career_batting_stat_award(award, stat_column="b_H", min_value=3000)
        elif career_stat == "40+ WAR Career (calculated)":
            results = get_players_career_war_award(award, 40)
        elif career_stat == "≤ 3.00 ERA Career Pitching (calculated)":
            results = get_players_career_era_team(award, 3.00)

    elif (option1 == "career statistic" and option2 == "positions") or (option1 == "positions" and option2 == "career statistic"):
        print("IN POSITION CSTATS")
        # Extract career statistics and team details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        position = option2_details if option1 == "career statistic" else option1_details

        # Handling different career statistics based on user input
        if career_stat == "300+ AVG Career Batting":
            results = get_players_careerBattingAVG_position(position, 0.300)
        elif career_stat == "200+ Wins Career Pitching":
            results = get_players_career_pitching_stat_position(position, stat_column="p_W", min_value=200)
        elif career_stat == "2000+ K Career Pitching":
            results = get_players_career_pitching_stat_position(position, stat_column="p_SO", min_value=2000)
        elif career_stat == "2000+ Hits Career Batting":
            results = get_players_career_batting_stat_position(position, stat_column="b_H", min_value=2000)
        elif career_stat == "300+ HR Career Batting":
            results = get_players_career_batting_stat_position(position, stat_column="b_HR", min_value=300)
        elif career_stat == "300+ Saves Career Pitching":
            results = get_players_career_pitching_stat_position(position, stat_column="p_SV", min_value=300)
        elif career_stat == "300+ Wins Career Pitching":
            results = get_players_career_pitching_stat_position(position, stat_column="p_W", min_value=300)
        elif career_stat == "3000+ K Career Pitching":
            results = get_players_career_pitching_stat_position(position, stat_column="p_SO", min_value=3000)
        elif career_stat == "3000+ Hits Career Batting":
            results = get_players_career_batting_stat_position(position, stat_column="b_H", min_value=3000)
        elif career_stat == "40+ WAR Career (calculated)":
            results = get_players_career_war_position(position, 40)
        elif career_stat == "≤ 3.00 ERA Career Pitching (calculated)":
            results = get_players_career_era_position(position, 3.00)

    elif (option1 == "career statistic" and option2 == "pob") or (option1 == "pob" and option2 == "career statistic"):
        print("IN POB CSTATS")
        # Extract career statistics and team details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        pob = option2_details if option1 == "career statistic" else option1_details

        # Handling different career statistics based on user input
        if career_stat == "300+ AVG Career Batting":
            results = get_players_careerBattingAVG_pob(0.300)
        elif career_stat == "200+ Wins Career Pitching":
            results = get_players_career_pitching_stat_pob(stat_column="p_W", min_value=200)
        elif career_stat == "2000+ K Career Pitching":
            results = get_players_career_pitching_stat_pob(stat_column="p_SO", min_value=2000)
        elif career_stat == "2000+ Hits Career Batting":
            results = get_players_career_batting_stat_pob(stat_column="b_H", min_value=2000)
        elif career_stat == "300+ HR Career Batting":
            results = get_players_career_batting_stat_pob(stat_column="b_HR", min_value=300)
        elif career_stat == "300+ Saves Career Pitching":
            results = get_players_career_pitching_stat_pob(stat_column="p_SV", min_value=300)
        elif career_stat == "300+ Wins Career Pitching":
            results = get_players_career_pitching_stat_pob(stat_column="p_W", min_value=300)
        elif career_stat == "3000+ K Career Pitching":
            results = get_players_career_pitching_stat_pob(stat_column="p_SO", min_value=3000)
        elif career_stat == "3000+ Hits Career Batting":
            results = get_players_career_batting_stat_pob(stat_column="b_H", min_value=3000)
        elif career_stat == "40+ WAR Career (calculated)":
            results = get_players_career_war_pob(40)
        elif career_stat == "≤ 3.00 ERA Career Pitching (calculated)":
            results = get_players_career_era_pob(3.00)

    elif (option1 == "awards" and option2 == "teams") or (option1 == "teams" and option2 == "awards"):
        # Extract the award and team details
        award = option1_details if option1 == "awards" else option2_details
        team = option1_details if option1 == "teams" else option2_details

        standard_awards = [
            "Gold Glove",
            "Cy Young Award",
            "Silver Slugger",
            "Rookie of the Year",
            "Most Valuable Player",
        ]
        if award in standard_awards:
            results = get_players_stdAward_team(award, team)

        elif award == "Hall of Fame":
            results = get_players_hof_team(team)

        elif award == "All Star":
            results = get_players_allstar_team(team)

        elif award == "World Series":
            results = get_players_ws_team(team)


    elif option1 == "awards" and option2 == "awards":
        standard_awards = [
            "Gold Glove",
            "Cy Young Award",
            "Silver Slugger",
            "Rookie of the Year",
            "Most Valuable Player",
        ]
        if option1_details in standard_awards and option2_details in standard_awards:
            results = get_players_stdAward_stdAward(option1_details, option2_details)



    elif (option1 == "positions" and option2 == "awards") or (option1 == "awards" and option2 == "positions"):
        position = option1_details if option1 == "positions" else option2_details
        award = option1_details if option1 == "awards" else option2_details

        standard_awards = [
            "Gold Glove",
            "Cy Young Award",
            "Silver Slugger",
            "Rookie of the Year",
            "Most Valuable Player",
        ]
        if award in standard_awards:
            results = get_players_stdAward_position(award, position)

        elif award == "Hall of Fame":
            results = get_players_hof_position(position)

        elif award == "All Star":
            results = get_players_allstar_position(position)


    elif (option1 == "seasonal statistic" and option2 == "awards") or (option1 == "awards" and option2 == "seasonal statistic"):
        if option1 == "awards":
            award = option1_details  # option1 holds the award details
            stat = option2_details  # option2 holds the stat details
        else:
            award = option2_details  # if option1 is not "award", then option2 must be "award"
            stat = option1_details  # if option2 is "award", then option1 must be "seasonal statistic"

        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "awards" else request.form.get(
            f'dropdown1_{stat}_specific')
        stat_range = int(stat_range.replace('+', ''))

        standard_awards = [
            "Gold Glove",
            "Cy Young Award",
            "Silver Slugger",
            "Rookie of the Year",
            "Most Valuable Player",
        ]
        standard_seasonStatBatting = [
            "HR",
            "RBI",
            "R",
            "H",
            "SB"
        ]

        if stat in standard_seasonStatBatting and award in standard_awards :
            results = get_players_seasonStatBatting_stdAward(stat, award, stat_range)
        elif stat in standard_seasonStatBatting and award == "World Series":
            results = get_players_seasonStatBatting_ws(stat, stat_range)
        elif stat in standard_seasonStatPitching and award in standard_awards:
            results = get_players_seasonStatPitching_stdAward(award, stat, stat_range)





    elif (option1 == "seasonal statistic" and option2 == "positions") or (option1 == "positions" and option2 == "seasonal statistic"):
        if option1 == "positions":
            position = option1_details
            stat = option2_details
        else:
            position = option2_details
            stat = option1_details

        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "positions" else request.form.get(
            f'dropdown1_{stat}_specific')
        stat_range = int(stat_range.replace('+', ''))
        if stat == "HR" or stat == "RBI" or stat == "R" or stat == "H" or stat == "SB":
            # Query for Home Runs (HR) greater than or equal to the selected range
            results = get_players_seasonStatBatting_position(stat, position, stat_range)



    elif (option1 == "teams" and option2 == "seasonal statistic") or (option1 == "seasonal statistic" and option2 == "teams"):
        if option1 == "teams":
            team = option1_details
            stat = option2_details
        else:
            team = option2_details
            stat = option1_details

        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "teams" else request.form.get(
            f'dropdown1_{stat}_specific')

        if stat == "HR" or stat == "RBI" or stat == "R" or stat == "H" or stat == "SB":
            stat_range = int(stat_range.replace('+', ''))
            results = get_players_seasonStatBatting_team(stat, team, stat_range)


        elif stat == "SV" or stat == "W" or stat == "SO":
            stat_range = int(stat_range.replace('+', ''))
            results = get_players_seasonStatPitching_team(stat, team, stat_range)

        elif stat == "AVG":
            stat_range = float(stat_range.replace('+', ''))
            results = get_players_seasonBattingAVG_team(stat_range, team)

        elif stat == "30+HR/30+SB":
            results = get_players_seasonBatting3030_team(team)



    elif option1 == "seasonal statistic" and option2 == "seasonal statistic":
        stat1 = option1_details
        stat2 = option2_details
        stat_range1 = request.form.get(f'dropdown1_{stat1}_specific')
        stat_range2 = request.form.get(f'dropdown2_{stat2}_specific')
        stat_range1 = int(stat_range1.replace('+', ''))
        stat_range2 = int(stat_range2.replace('+', ''))

        if stat1 in standard_seasonStatBatting and stat2 in standard_seasonStatBatting:
            results = get_players_seasonStatPitching_seasonStatPitching(stat1, stat_range1, stat2, stat_range2)

        elif (stat1 in standard_seasonStatBatting or stat1 in standard_seasonStatPitching) and (stat2 in standard_seasonStatBatting or stat2 in standard_seasonStatPitching):
            if stat1 in standard_seasonStatBatting:
                results = get_players_seasonStatPitching_seasonStatBatting(stat2, stat_range2, stat1, stat_range1)
            else:
                results = get_players_seasonStatPitching_seasonStatBatting(stat1, stat_range1, stat2, stat_range2)



    elif (option1 == "pob" and option2 == "teams") or (option1 == "teams" and option2 == "pob"):
        team= option1_details if option1 == "teams" else option2_details
        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(Appearances, Appearances.playerID == People.playerID)  # Join Appearances to get team info
            .join(Teams, Teams.teamID == Appearances.teamID)  # Join Teams to filter by team
            .filter(
                Teams.team_name == team,  # Filter for the specified team
                People.birthCountry != "USA"  # Exclude players born in the United States
            )
            .group_by(People.playerID)  # Group by player to calculate total appearances
            .order_by(db.func.sum(Appearances.G_all).asc())  # Sort by the least total appearances
            .all()
        )
    elif (option1 == "pob" and option2 == "positions") or (option1 == "positions" and option2 == "pob"):
        position = option1_details if option1 == "positions" else option2_details
        results = get_players_pob_position(position)


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