from flask import Blueprint, request, render_template
from sqlalchemy import func

from app.models import People, Batting, Teams, db, Fielding, Awards, HallOfFame, AllStarFull, Appearances, Pitching, \
    SeriesPost, FieldingPost, BattingPost, Drafts

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

def get_players_position_position(position1, position2):
    position_column1 = f'G_{position1.lower()}'
    position_column2 = f'G_{position2.lower()}'

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(getattr(Appearances, position_column1) > 0)
        .filter(getattr(Appearances, position_column2) > 0)
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
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

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(
            People.birthCountry != 'USA', getattr(Appearances, position_column) > 0 )
        .group_by(People.playerID)  # Group by player ID to calculate total appearances
        .order_by(func.sum(getattr(Appearances, position_column)))
        .distinct()
        .all()
    )

def get_players_draftPick_position(position):
    position_column = f'G_{position.lower()}'

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(Drafts.draft_round == 1)
        .filter(getattr(Appearances, position_column) > 0 )
        .group_by(People.playerID)  # Group by player ID to calculate total appearances
        .order_by(func.sum(getattr(Appearances, position_column)))
        .distinct()
        .all()
    )


def get_players_pob_hof():
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .filter(People.birthCountry != 'USA')
        .filter(HallOfFame.inducted == "Y")
        .group_by(People.playerID)
        .order_by(func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )

def get_players_pob_allStar():
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .filter(People.birthCountry != 'USA')
        .filter(AllStarFull.GP > 0)
        .group_by(People.playerID)
        .order_by(func.sum(AllStarFull.GP).asc())
        .distinct()
        .all()
    )

def get_players_pob_stdAward(award):
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(People.birthCountry != 'USA')
        .filter(Awards.awardID == award)
        .group_by(People.playerID)
        .order_by(func.sum(Appearances.G_all).asc())
        .distinct()
        .all()

    )



"""
get_players_seasonStatBatting_ws
queries for a player that is in the world series winning roster and 
has this season batting stat. does not need to be in the same season as the world series
takes in a stat_column, and stat_range
algorithm orders it by least appearances in batting b_G
"""
def get_players_seasonStatBatting_ws(stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    season_stat = (
        db.session.query(
            Batting.playerID,
            Batting.teamID
        )
        .filter(batting_column >= stat_range)
        .subquery()
    )
    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(season_stat, season_stat.c.playerID == People.playerID)  # Join with season stats subquery
        .join(Batting, Batting.playerID == season_stat.c.playerID)  # Join with Batting for team data
        .join(SeriesPost, SeriesPost.teamIDwinner == season_stat.c.teamID)  # Join with SeriesPost for WS-winning teams
        .filter(SeriesPost.round == "WS")  # Filter for World Series round
        .filter(SeriesPost.teamIDwinner == season_stat.c.teamID)  # Ensure stat was achieved while on a WS-winning team
        .group_by(People.playerID)  # Group by player
        .order_by(db.func.sum(Batting.b_G).asc())  # Order by least total appearances
        .distinct()  # Ensure distinct players
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

def get_players_seasonBattingAVG_stdAward(stat_range, award):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter((Batting.b_H/ Batting.b_AB) >= stat_range)  # Batting average of .300 or higher
        .filter(Awards.awardID == award)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonBatting3030_stdAward(award):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .filter(Awards.awardID == award)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonBattingAVG_allStar(stat_range):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .filter((Batting.b_H/ Batting.b_AB) >= stat_range)  # Batting average of .300 or higher
        .filter(AllStarFull.GP > 0)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonBattingAVG_hof(stat_range):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .filter((Batting.b_H/ Batting.b_AB) >= stat_range)  # Batting average of .300 or higher
        .filter(HallOfFame.inducted == 'Y')
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
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )


def get_players_seasonStatBatting3030_seasonStatBatting(batting_column, batting_range):
    batting_column1 = getattr(Batting, f"b_{batting_column}")
    batting_subquery = (
        db.session.query(Batting.playerID)
        .filter(batting_column1 >= batting_range)
        .subquery()
    )
    thirty_subquery = (
        db.session.query(Batting.playerID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .subquery()

    )

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(batting_subquery, batting_subquery.c.playerID == People.playerID)
        .join(thirty_subquery, thirty_subquery.c.playerID == People.playerID)
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

def get_players_seasonStatERA_stdAward(award):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(
            Pitching.p_ERA <= 3.00,
            Awards.awardID == award  # Check if the player won the specified award
        )
        .group_by(People.playerID)  # Group by player to ensure distinct results
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


def get_players_seasonStatBatting_position(stat_column, position, stat_range):
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'
    batting_column = getattr(Batting, f"b_{stat_column}")

    return (
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

def get_players_seasonBattingAVG_position(position, stat_range):
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter((Batting.b_H/Batting.b_AB) >= stat_range)
        .filter(getattr(Appearances, position_column) > 0 )
        .group_by(People.playerID)  # Group by player ID to calculate total appearances
        .order_by(func.sum(getattr(Appearances, position_column)))
        .distinct()
        .all()
    )

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

def get_players_seasonStatBatting_pob(stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(batting_column >= stat_range)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonStatPitching_pob(stat_column, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(pitching_column >= stat_range)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


def get_players_careerBattingAVG_team(stat_range, team):
    # Subquery: Get player IDs of players who played at least one game for the given team
    played_for_team = (
        db.session.query(Batting.playerID)
        .join(Teams, Teams.teamID == Batting.teamID)
        .filter(Teams.team_name == team)  # Use correct column for team name
        .group_by(Batting.playerID)
        .subquery()
    )

    # Main query: Calculate career batting average for players in the subquery
    return (
        db.session.query(
            People.nameFirst,
            People.nameLast  # Only select first and last name
        )
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.playerID.in_(played_for_team))  # Filter only players from the subquery
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(db.func.sum(Batting.b_AB) > 0)  # Ensure no division by zero
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)  # Apply average filter
        .order_by(db.func.sum(Batting.b_G).asc())  # Order by least games played
        .all()
    )

def get_players_careerBattingAVG_stdAward(stat_range, award):
    # Subquery: Get player IDs of players who played at least one game for the given team
    won_stdAward = (
        db.session.query(Awards.playerID)
        .filter(Awards.awardID == award)  # Use correct column for team name
        .group_by(Awards.playerID)
        .subquery()
    )

    # Main query: Calculate career batting average for players in the subquery
    return (
        db.session.query(
            People.nameFirst,
            People.nameLast  # Only select first and last name
        )
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.playerID.in_(won_stdAward))  # Filter only players from the subquery
        .group_by(People.playerID)
        .having(db.func.sum(Batting.b_AB) > 0)  # Ensure no division by zero
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)  # Apply average filter
        .order_by(db.func.sum(Batting.b_G).asc())  # Order by least games played
        .distinct()
        .all()
    )

def get_players_careerBattingAVG_hof(stat_range):
    in_hof = (
        db.session.query(HallOfFame.playerID)
        .filter(HallOfFame.inducted == 'Y')
        .group_by(HallOfFame.playerID)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast  # Only select first and last name
        )
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.playerID.in_(db.select(in_hof.c.playerID)))  # Filter only players from the subquery
        .group_by(People.playerID)
        .having(db.func.sum(Batting.b_AB) > 0)  # Ensure no division by zero
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)  # Apply average filter
        .order_by(db.func.sum(Batting.b_G).asc())  # Order by least games played
        .distinct()
        .all()
    )


def get_players_careerBattingAVG_allStar(stat_range):
    in_allStar = (
        db.session.query(AllStarFull.playerID)
        .filter(AllStarFull.GP > 0)
        .group_by(AllStarFull.playerID)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast  # Only select first and last name
        )
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.playerID.in_(db.select(in_allStar.c.playerID))) # Filter only players from the subquery
        .group_by(People.playerID)
        .having(db.func.sum(Batting.b_AB) > 0)  # Ensure no division by zero
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)  # Apply average filter
        .order_by(db.func.sum(Batting.b_G).asc())  # Order by least games played
        .distinct()
        .all()
    )

def get_players_careerBattingAVG_position(stat_range, position):
    position_column = f'G_{position.lower()}'

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast  # Only select first and last name
        )
        .join(Batting, Batting.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(getattr(Appearances, position_column) > 0)
        .group_by(People.playerID)
        .having(db.func.sum(Batting.b_AB) > 0)  # Ensure no division by zero
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)  # Apply average filter
        .order_by(db.func.sum(getattr(Appearances, position_column)).asc())  # Order by least games played
        .distinct()
        .all()
    )

def get_players_careerStatBatting_position(stat_column, stat_range, position):
    batting_column = getattr(Batting, f"b_{stat_column}")
    total_stat = db.func.sum(batting_column).label('total_stat')
    position_column = f'G_{position.lower()}'

    career_stats= (
        db.session.query(
            Batting.playerID,
            total_stat
        )
        .group_by(Batting.playerID)
        .having(total_stat > stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(getattr(Appearances, position_column) > 0)
        .group_by(People.playerID)
        .order_by(db.func.sum(getattr(Appearances, position_column)).asc())
        .distinct()
        .all()

    )






"""
get_players_careerStatBatting_team
Queries a player that achieved a batting stat while playing for a team over their entire career.
Takes in a team, the stat_column, and the stat range.
Algorithm uses the batting table to calculate career totals and orders by least total appearances (b_G).
"""
def get_players_careerStatBatting_team(stat_column, team, stat_range):
    # Define aliases and columns for the query
    batting_column = getattr(Batting, f"b_{stat_column}")  # Get the relevant batting column for stats
    total_stat = db.func.sum(batting_column).label("total_stat")  # Calculate the total for the stat

    # Subquery to calculate career totals for all players
    career_stats = (
        db.session.query(
            Batting.playerID,
            total_stat
        )
        .group_by(Batting.playerID)  # Group by player for career totals
        .having(total_stat > stat_range)  # Filter for players with stat total above the range
        .subquery()  # Create a subquery
    )

    # Main query to filter by team and return the desired results
    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)  # Join with career totals
        .join(Batting, Batting.playerID == People.playerID)  # Join Batting for player stats
        .join(Teams, Teams.teamID == Batting.teamID)  # Join Teams to filter by team
        .filter(Teams.team_name == team)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()  # Ensure distinct players
        .all()
    )

def get_players_careerStatPitching_team(stat_column, team, stat_range):
    # Define aliases and columns for the query
    pitching_column = getattr(Pitching, f"p_{stat_column}")  # Get the relevant batting column for stats
    total_stat = db.func.sum(pitching_column).label("total_stat")  # Calculate the total for the stat

    # Subquery to calculate career totals for all players
    career_stats = (
        db.session.query(
            Pitching.playerID,
            total_stat
        )
        .group_by(Pitching.playerID)  # Group by player for career totals
        .having(total_stat > stat_range)  # Filter for players with stat total above the range
        .subquery()  # Create a subquery
    )

    # Main query to filter by team and return the desired results
    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)  # Join with career totals
        .join(Pitching, Pitching.playerID == People.playerID)  # Join Batting for player stats
        .join(Teams, Teams.teamID == Pitching.teamID)  # Join Teams to filter by team
        .filter(Teams.team_name == team)  # Filter by the specified team
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()  # Ensure distinct players
        .all()
    )

def get_players_careerStatPitching_hof(stat_column, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    total_stat = db.func.sum(pitching_column).label("total_stat")

    career_stats = (
        db.session.query(
            Pitching.playerID,
            total_stat
        )
        .group_by(Pitching.playerID)
        .having(total_stat > stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID )
        .filter(HallOfFame.inducted == "Y")
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()  # Ensure distinct players
        .all()
    )

def get_players_careerStatBatting_hof(stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    total_stat = db.func.sum(batting_column).label("total_stat")

    career_stats = (
        db.session.query(
            Batting.playerID,
            total_stat
        )
        .group_by(Batting.playerID)
        .having(total_stat > stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Batting, Batting.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID )
        .filter(HallOfFame.inducted == "Y")
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()  # Ensure distinct players
        .all()
    )


def get_players_careerStatPitching_allStar(stat_column, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    total_stat = db.func.sum(pitching_column).label("total_stat")

    career_stats = (
        db.session.query(
            Pitching.playerID,
            total_stat
        )
        .group_by(Pitching.playerID)
        .having(total_stat > stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(AllStarFull, AllStarFull.playerID == People.playerID )
        .filter(AllStarFull.GP > 0)
        .group_by(People.playerID)
        .order_by(db.func.sum(AllStarFull.GP).asc())
        .distinct()
        .all()
    )

def get_players_careerStatBatting_allStar(stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    total_stat = db.func.sum(batting_column).label("total_stat")

    career_stats = (
        db.session.query(
            Batting.playerID,
            total_stat
        )
        .group_by(Batting.playerID)
        .having(total_stat > stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(AllStarFull, AllStarFull.playerID == People.playerID )
        .filter(AllStarFull.GP > 0)
        .group_by(People.playerID)
        .order_by(db.func.sum(AllStarFull.GP).asc())
        .distinct()
        .all()
    )

def get_players_careerStatbatting_allStar(stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    total_stat = db.func.sum(batting_column).label("total_stat")

    career_stats = (
        db.session.query(
            Batting.playerID,
            total_stat
        )
        .group_by(Batting.playerID)
        .having(total_stat > stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Batting, Batting.playerID == People.playerID)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .filter(AllStarFull.GP > 0)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()  # Ensure distinct players
        .all()
    )



def get_players_careerStatPitching_stdAward(stat_column, award, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    total_stat = db.func.sum(pitching_column).label("total_stat")

    career_stats = (
        db.session.query(
            Pitching.playerID,
            total_stat
        )
        .group_by(Pitching.playerID)
        .having(total_stat > stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(Awards.awardID == award)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()  # Ensure distinct players
        .all()
    )

def get_players_careerStatBatting_stdAward(stat_column, award, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    total_stat = db.func.sum(batting_column).label("total_stat")

    career_stats = (
        db.session.query(
            Batting.playerID,
            total_stat
        )
        .group_by(Batting.playerID)
        .having(total_stat > stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(Awards.awardID == award)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()  # Ensure distinct players
        .all()
    )

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


def get_players_seasonStatBatting_seasonStatBatting(stat_column1, stat_range1, stat_column2, stat_range2):
    batting_column1 = getattr(Batting, f"b_{stat_column1}")
    batting_column2 = getattr(Batting, f"b_{stat_column2}")

    # Subqueries to check for each stat independently
    stat1_subquery = (
        db.session.query(Batting.playerID)
        .filter(batting_column1 >= stat_range1)
        .subquery()
    )
    stat2_subquery = (
        db.session.query(Batting.playerID)
        .filter(batting_column2 >= stat_range2)
        .subquery()
    )

    # Main query: find players present in both subqueries
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(stat1_subquery, stat1_subquery.c.playerID == People.playerID)
        .join(stat2_subquery, stat2_subquery.c.playerID == People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .group_by(People.playerID)
        .distinct()
        .all()
    )


def get_players_careerStatBatting_careerStatBatting(stat_column1, stat_range1, stat_column2, stat_range2):
    batting_column1 = getattr(Batting, f"b_{stat_column1}")
    batting_column2 = getattr(Batting, f"b_{stat_column2}")

    # Subqueries to check for each stat independently
    stat1_subquery = (
        db.session.query(Batting.playerID)
        .group_by(Batting.playerID)
        .having(db.func.sum(batting_column1) >= stat_range1)
        .subquery()
    )
    stat2_subquery = (
        db.session.query(Batting.playerID)
        .group_by(Batting.playerID)
        .having(db.func.sum(batting_column2) >= stat_range2)
        .subquery()
    )

    # Main query: find players present in both subqueries
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(stat1_subquery, stat1_subquery.c.playerID == People.playerID)
        .join(stat2_subquery, stat2_subquery.c.playerID == People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .group_by(People.playerID)
        .distinct()
        .all()
    )


def get_players_careerStatBatting_careerStatPitching(batting_column1, batting_range1, pitching_column2, pitching_range2):
    batting_column1 = getattr(Batting, f"b_{batting_column1}")
    pitching_column2 = getattr(Pitching, f"p_{pitching_column2}")

    # Subqueries to check for each stat independently
    stat1_subquery = (
        db.session.query(Batting.playerID)
        .group_by(Batting.playerID)
        .having(db.func.sum(batting_column1) >= batting_range1)
        .subquery()
    )
    stat2_subquery = (
        db.session.query(Pitching.playerID)
        .group_by(Pitching.playerID)
        .having(db.func.sum(pitching_column2) >= pitching_range2)
        .subquery()
    )

    # Main query: find players present in both subqueries
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(stat1_subquery, stat1_subquery.c.playerID == People.playerID)
        .join(stat2_subquery, stat2_subquery.c.playerID == People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .group_by(People.playerID)
        .distinct()
        .all()
    )

def get_players_careerBattingAVG_careerStatBatting(avg_range, stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")

    # Subqueries to check for each stat independently
    stat1_subquery = (
        db.session.query(Batting.playerID)
        .group_by(Batting.playerID)
        .having(db.func.sum(batting_column) >= stat_range)
        .subquery()
    )
    avg_subquery = (
        db.session.query(Batting.playerID)
        .group_by(Batting.playerID)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= avg_range)
        .subquery()
    )

    # Main query: find players present in both subqueries
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(stat1_subquery, stat1_subquery.c.playerID == People.playerID)
        .join(avg_subquery, avg_subquery.c.playerID == People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .group_by(People.playerID)
        .distinct()
        .all()
    )





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

def get_players_seasonStatPitching_allStar(stat_column, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .filter(AllStarFull.GP > 0)
        .filter(pitching_column >= stat_range)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


def get_players_seasonStatBatting_allStar(stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .filter(AllStarFull.GP > 0)
        .filter(batting_column >= stat_range)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonStatBatting_hof(stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .filter(batting_column >= stat_range)
        .filter(HallOfFame.inducted == 'Y')
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonStatPitching_hof(stat_column, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .filter(pitching_column >= stat_range)
        .filter(HallOfFame.inducted == 'Y')
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

def get_players_seasonStatPitching_seasonStatAVG(pitching_column, pitching_range, avg_range):
    pitching_column1 = getattr(Pitching, f"p_{pitching_column}")
    pitching_subquery = (
        db.session.query(Pitching.playerID)
        .filter(pitching_column1 >= pitching_range)
        .subquery()
    )
    avg_subquery = (
        db.session.query(Batting.playerID)
        .filter((Batting.b_H/Batting.b_AB) >= avg_range)
        .subquery()

    )

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(pitching_subquery, pitching_subquery.c.playerID == People.playerID)
        .join(avg_subquery, avg_subquery.c.playerID == People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .group_by(People.playerID)
        .distinct()
        .all()
    )

def get_players_seasonStatBatting_seasonStatAVG(batting_column, batting_range, avg_range):
    batting_column1 = getattr(Batting, f"b_{batting_column}")
    batting_subquery = (
        db.session.query(Batting.playerID)
        .filter(batting_column1 >= batting_range)
        .subquery()
    )
    avg_subquery = (
        db.session.query(Batting.playerID)
        .filter((Batting.b_H/Batting.b_AB) >= avg_range)
        .subquery()

    )

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(batting_subquery, batting_subquery.c.playerID == People.playerID)
        .join(avg_subquery, avg_subquery.c.playerID == People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .group_by(People.playerID)
        .distinct()
        .all()
    )


def get_players_careerStatBatting_seasonStatBatting(career_column, career_range, season_column, season_range):
    career_column1 = getattr(Batting, f"b_{career_column}")
    season_column1 = getattr(Batting, f"b_{season_column}")

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Batting.playerID
        )
        .group_by(Batting.playerID)  # Group by player for aggregation
        .having(db.func.sum(career_column1) >= career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter(season_column1 >= season_range)  # Per-season filter
        .group_by(Batting.playerID)
        .subquery()
    )

    # Main query to find players matching both criteria
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(career_subquery, career_subquery.c.playerID == People.playerID)
        .join(season_subquery, season_subquery.c.playerID == People.playerID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )


def get_players_careerStatPitching_seasonStatPitching(career_column, career_range, season_column, season_range):
    career_column1 = getattr(Pitching, f"p_{career_column}")
    season_column1 = getattr(Pitching, f"p_{season_column}")

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Pitching.playerID
        )
        .group_by(Pitching.playerID)  # Group by player for aggregation
        .having(db.func.sum(career_column1) >= career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Pitching.playerID
        )
        .filter(season_column1 >= season_range)  # Per-season filter
        .group_by(Pitching.playerID)
        .subquery()
    )

    # Main query to find players matching both criteria
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(career_subquery, career_subquery.c.playerID == People.playerID)
        .join(season_subquery, season_subquery.c.playerID == People.playerID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )




def get_players_seasonStatBatting_team(stat, team, stat_range):
    batting_column1 = getattr(Batting, f"b_{stat}")
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Teams, Teams.teamID == Batting.teamID)
        .filter(Teams.team_name == team)
        .filter(batting_column1 >= stat_range)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_draftPick_hof():
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(HallOfFame.inducted == 'Y')
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
    )

def get_players_draftPick_allStar():
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(AllStarFull.GP > 0)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(AllStarFull.GP).asc())
    )




@bp.route('/search_players', methods=['POST'])
def search_players():
    standard_seasonStatBatting = [
        "HR",
        "RBI",
        "R",
        "H",
        "SB"
    ]
    standard_careerStatBatting = [
        "HR",
        "H"
    ]

    standard_seasonStatPitching = [
        "SV",
        "W",
        "SO"
    ]
    standard_careerStatPitching = [
        "SV",
        "W",
        "SO"
    ]

    standard_awards = [
        "Gold Glove",
        "Cy Young Award",
        "Silver Slugger",
        "Rookie of the Year",
        "Most Valuable Player",
    ]

    def convert_to_number(value):
        value = value.replace('+', '')  # Remove the '+' if it exists
        try:
            if '.' in value:
                return float(value)  # Convert to float if it contains a decimal point
            return int(value)  # Otherwise, convert to int
        except ValueError:
            raise ValueError(f"Invalid number format: {value}")

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

    elif (option1 == "career statistic" and option2 == "teams") or (option1 == "teams" and option2 == "career statistic"):
        print("IN TEAMS CSTATS")
        # Extract career statistics and team details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        team = option2_details if option1 == "career statistic" else option1_details
        stat_range = request.form.get(f'dropdown2_{career_stat}_specific') if option1 == "teams" else request.form.get(
            f'dropdown1_{career_stat}_specific')

        stat_range = convert_to_number(stat_range)

        # Handling different career statistics based on user input
        if career_stat == "AVG":
            results = get_players_careerBattingAVG_team(stat_range, team)
        elif career_stat in standard_careerStatBatting:
            results = get_players_careerStatBatting_team(career_stat, team, stat_range)
        elif career_stat in standard_careerStatPitching:
            print("Harrison Here")
            results = get_players_careerStatPitching_team(career_stat, team, stat_range)

    elif (option1 == "teams" and option2 == "seasonal statistic") or (option1 == "seasonal statistic" and option2 == "teams"):
        if option1 == "teams":
            team = option1_details
            stat = option2_details
        else:
            team = option2_details
            stat = option1_details

        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "teams" else request.form.get(
            f'dropdown1_{stat}_specific')

        if stat in standard_seasonStatBatting:
            stat_range = int(stat_range.replace('+', ''))
            results = get_players_seasonStatBatting_team(stat, team, stat_range)


        elif stat in standard_seasonStatPitching:
            stat_range = int(stat_range.replace('+', ''))
            results = get_players_seasonStatPitching_team(stat, team, stat_range)

        elif stat == "AVG":
            stat_range = float(stat_range.replace('+', ''))
            results = get_players_seasonBattingAVG_team(stat_range, team)

        elif stat == "30+HR/30+SB":
            results = get_players_seasonBatting3030_team(team)


    elif (option1 == "awards" and option2 == "teams") or (option1 == "teams" and option2 == "awards"):
        # Extract the award and team details
        award = option1_details if option1 == "awards" else option2_details
        team = option1_details if option1 == "teams" else option2_details

        if award in standard_awards:
            results = get_players_stdAward_team(award, team)

        elif award == "Hall of Fame":
            results = get_players_hof_team(team)

        elif award == "All Star":
            results = get_players_allstar_team(team)

        elif award == "World Series":
            results = get_players_ws_team(team)

    elif (option1 == "positions" and option2 == "teams") or (option1 == "teams" and option2 == "positions"):
        # Extract the position and team details
        position = option1_details if option1 == "positions" else option2_details
        team = option1_details if option1 == "teams" else option2_details
        results = get_players_position_team(position, team)

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

    elif option1 == "career statistic" and option2 == "career statistic":
        stat1 = option1_details
        stat2 = option2_details
        stat_range1 = request.form.get(f'dropdown1_{stat1}_specific')
        stat_range2 = request.form.get(f'dropdown2_{stat2}_specific')



        stat_range1 = convert_to_number(stat_range1)
        stat_range2 = convert_to_number(stat_range2)

        if stat1 in standard_careerStatBatting and stat2 in standard_careerStatBatting:
            results = get_players_careerStatBatting_careerStatBatting(stat1, stat_range1, stat2, stat_range2)
        if (stat1 in standard_careerStatBatting and stat2 in standard_careerStatPitching) or (stat1 in standard_careerStatPitching and stat2 in standard_careerStatBatting):
            if stat1 in standard_careerStatBatting:
                results = get_players_careerStatBatting_careerStatPitching(stat1, stat_range1, stat2, stat_range2)
            else:
                results = get_players_careerStatBatting_careerStatPitching(stat2, stat_range2, stat1, stat_range1)

        if (stat1 == "AVG" and stat2 in standard_careerStatBatting) or (stat1 in standard_careerStatBatting and stat2 == "AVG"):
            if stat1 == "AVG":
                results = get_players_careerBattingAVG_careerStatBatting(stat_range1, stat2, stat_range2)
            else:
                results = get_players_careerBattingAVG_careerStatBatting(stat_range2, stat1, stat_range1)

    elif (option1 == "career statistic" and option2 == "seasonal statistic") or \
            (option1 == "seasonal statistic" and option2 == "career statistic"):
        # Determine which is career and which is seasonal
        if option1 == "career statistic":
            career_stat, seasonal_stat = option1_details, option2_details
            career_range = request.form.get(f'dropdown1_{career_stat}_specific')
            seasonal_range = request.form.get(f'dropdown2_{seasonal_stat}_specific')
        else:
            seasonal_stat, career_stat = option1_details, option2_details
            seasonal_range = request.form.get(f'dropdown1_{seasonal_stat}_specific')
            career_range = request.form.get(f'dropdown2_{career_stat}_specific')

        # Convert ranges
        career_range1 = convert_to_number(career_range)
        seasonal_range2 = convert_to_number(seasonal_range)

        # Check statistics and fetch results
        if career_stat in standard_careerStatBatting and seasonal_stat in standard_seasonStatBatting:
            results = get_players_careerStatBatting_seasonStatBatting(career_stat, career_range1, seasonal_stat, seasonal_range2)
        elif career_stat in standard_careerStatPitching and seasonal_stat in standard_seasonStatPitching:
            results = get_players_careerStatPitching_seasonStatPitching(career_stat, career_range1, seasonal_stat, seasonal_range2)






    elif (option1 == "career statistic" and option2 == "awards") or (option1 == "awards" and option2 == "career statistic"):
        print("IN AWARDS CSTATS")
        # Extract the award and career statistic details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        award = option2_details if option1 == "career statistic" else option1_details
        stat_range = request.form.get(f'dropdown2_{career_stat}_specific') if option1 == "awards" else request.form.get(f'dropdown1_{career_stat}_specific')
        stat_range = convert_to_number(stat_range)

        # Handling different career statistics based on user input
        if award == "Hall of Fame" and career_stat in standard_careerStatPitching:
            results = get_players_careerStatPitching_hof(career_stat, stat_range)
        elif award == "Hall of Fame" and career_stat in standard_careerStatBatting:
            results = get_players_careerStatBatting_hof(career_stat, stat_range)
        elif award == "All Star" and career_stat in standard_careerStatPitching:
            results = get_players_careerStatPitching_allStar(career_stat, stat_range)
        elif award == "All Star" and career_stat in standard_careerStatBatting:
            results = get_players_careerStatBatting_allStar(career_stat, stat_range)
        elif award in standard_awards and career_stat in standard_careerStatPitching:
            results = get_players_careerStatPitching_stdAward(career_stat, award, stat_range)
        elif award in standard_awards and career_stat in standard_careerStatBatting:
            results = get_players_careerStatBatting_stdAward(career_stat, award, stat_range)
        elif career_stat == "AVG" and award in standard_awards:
            results = get_players_careerBattingAVG_stdAward(stat_range, award)
        elif career_stat == "AVG" and award == "Hall of Fame":
            results = get_players_careerBattingAVG_hof(stat_range)
        elif career_stat == "AVG" and award == "All Star":
            results = get_players_careerBattingAVG_allStar(stat_range)





    elif (option1 == "career statistic" and option2 == "positions") or (option1 == "positions" and option2 == "career statistic"):
        print("IN POSITION CSTATS")
        # Extract career statistics and team details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        position = option2_details if option1 == "career statistic" else option1_details
        stat_range = request.form.get(f'dropdown2_{career_stat}_specific') if option1 == "awards" else request.form.get(
            f'dropdown1_{career_stat}_specific')
        stat_range = convert_to_number(stat_range)

        if career_stat == "AVG":
            results = get_players_careerBattingAVG_position(stat_range, position)
        if career_stat in standard_careerStatBatting:
            results = get_players_careerStatBatting_position(career_stat, stat_range, position)


    elif (option1 == "career statistic" and option2 == "pob") or (option1 == "pob" and option2 == "career statistic"):
        print("IN POB CSTATS")
        # Extract career statistics and team details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        pob = option2_details if option1 == "career statistic" else option1_details


    elif option1 == "seasonal statistic" and option2 == "seasonal statistic":
        stat1 = option1_details
        stat2 = option2_details


        stat_range1 = request.form.get(f'dropdown1_{stat1}_specific')
        stat_range2 = request.form.get(f'dropdown2_{stat2}_specific')

        if stat_range1 != "30+HR/30+SB":
            stat_range1 = convert_to_number(stat_range1)

        if stat_range2 != "30+HR/30+SB":
            stat_range2 = convert_to_number(stat_range2)

        if stat1 in standard_seasonStatBatting and stat2 in standard_seasonStatBatting:
            results = get_players_seasonStatBatting_seasonStatBatting(stat1, stat_range1, stat2, stat_range2)

        elif (stat1 in standard_seasonStatBatting or stat1 in standard_seasonStatPitching) and (stat2 in standard_seasonStatBatting or stat2 in standard_seasonStatPitching):
            if stat1 in standard_seasonStatBatting:
                results = get_players_seasonStatPitching_seasonStatBatting(stat2, stat_range2, stat1, stat_range1)
            else:
                results = get_players_seasonStatPitching_seasonStatBatting(stat1, stat_range1, stat2, stat_range2)
        elif (stat1 in standard_seasonStatPitching and stat2 == "AVG") or (stat1 == "AVG" and stat2 in standard_seasonStatPitching):
            if stat1 in standard_seasonStatPitching:
                results = get_players_seasonStatPitching_seasonStatAVG(stat1, stat_range1, stat_range2)
            else:
                results = get_players_seasonStatPitching_seasonStatAVG(stat2, stat_range2, stat_range1)
        elif (stat1 in standard_seasonStatBatting and stat2 == "AVG") or (stat1 == "AVG" and stat2 in standard_seasonStatBatting):
            if stat1 in standard_seasonStatBatting:
                results = get_players_seasonStatBatting_seasonStatAVG(stat1, stat_range1, stat_range2)
            else:
                results = get_players_seasonStatBatting_seasonStatAVG(stat2, stat_range2, stat_range1)

        elif (stat1 in standard_seasonStatBatting and stat2 == "30+HR/30+SB") or (stat1 == "30+HR/30+SB" and stat2 in standard_seasonStatBatting):
            if stat1 == "30+HR/30+SB":
                results = get_players_seasonStatBatting3030_seasonStatBatting(stat2, stat_range2)
            else:
                results = get_players_seasonStatBatting3030_seasonStatBatting(stat1, stat_range1)


    elif (option1 == "seasonal statistic" and option2 == "awards") or (option1 == "awards" and option2 == "seasonal statistic"):
        if option1 == "awards":
            award = option1_details  # option1 holds the award details
            stat = option2_details  # option2 holds the stat details
        else:
            award = option2_details  # if option1 is not "award", then option2 must be "award"
            stat = option1_details  # if option2 is "award", then option1 must be "seasonal statistic"

        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "awards" else request.form.get(
            f'dropdown1_{stat}_specific')
        if stat != "ERA" and stat != "30+HR/30+SB":
            stat_range = convert_to_number(stat_range)


        if stat in standard_seasonStatBatting and award in standard_awards :
            results = get_players_seasonStatBatting_stdAward(stat, award, stat_range)
        elif stat in standard_seasonStatPitching and award in standard_awards:
            results = get_players_seasonStatPitching_stdAward(award, stat, stat_range)
        elif stat in standard_seasonStatBatting and award == "World Series":
            results = get_players_seasonStatBatting_ws(stat, stat_range)
        elif stat in standard_seasonStatBatting and award == "All Star":
            results = get_players_seasonStatBatting_allStar(stat, stat_range)
        elif stat in standard_seasonStatPitching and award == "All Star":
            results = get_players_seasonStatPitching_allStar(stat, stat_range)
        elif stat == "AVG" and award in standard_awards:
            results = get_players_seasonBattingAVG_stdAward(stat_range, award)
        elif stat == "AVG" and award == "All Star":
            results = get_players_seasonBattingAVG_allStar(stat_range)
        elif stat == "AVG" and award == "Hall of Fame":
            results = get_players_seasonBattingAVG_hof(stat_range)
        elif stat in standard_seasonStatBatting and award == "Hall of Fame":
            results = get_players_seasonStatBatting_hof(stat, stat_range)
        elif stat in standard_seasonStatPitching and award == "Hall of Fame":
            results = get_players_seasonStatPitching_hof(stat, stat_range)
        elif stat == "ERA" and award in standard_awards:
            results = get_players_seasonStatERA_stdAward(award)
        elif stat == "30+HR/30+SB" and award in standard_awards:
            results = get_players_seasonBatting3030_stdAward(award)


    elif (option1 == "seasonal statistic" and option2 == "positions") or (option1 == "positions" and option2 == "seasonal statistic"):
        if option1 == "positions":
            position = option1_details
            stat = option2_details
        else:
            position = option2_details
            stat = option1_details

        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "positions" else request.form.get(
            f'dropdown1_{stat}_specific')
        stat_range = convert_to_number(stat_range)
        if stat in standard_seasonStatBatting:
            results = get_players_seasonStatBatting_position(stat, position, stat_range)
        if stat == "AVG":
            results = get_players_seasonBattingAVG_position(position, stat_range)


    elif (option1 == "seasonal statistic" and option2 == "pob") or (option1 == "pob" and option2 == "seasonal statistic"):
        stat = option1_details if option1 == "seasonal statistic" else option2_details
        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "pob" else request.form.get(
            f'dropdown1_{stat}_specific')
        stat_range = convert_to_number(stat_range)

        if stat in standard_seasonStatBatting:
            results = get_players_seasonStatBatting_pob(stat, stat_range)
        elif stat in standard_seasonStatPitching:
            results = get_players_seasonStatPitching_pob(stat, stat_range)



    elif option1 == "awards" and option2 == "awards":
        if option1_details in standard_awards and option2_details in standard_awards:
            results = get_players_stdAward_stdAward(option1_details, option2_details)



    elif (option1 == "positions" and option2 == "awards") or (option1 == "awards" and option2 == "positions"):
        position = option1_details if option1 == "positions" else option2_details
        award = option1_details if option1 == "awards" else option2_details

        if award in standard_awards:
            results = get_players_stdAward_position(award, position)

        elif award == "Hall of Fame":
            results = get_players_hof_position(position)

        elif award == "All Star":
            results = get_players_allstar_position(position)

    elif (option1 == "pob" and option2 == "awards") or (option1 == "awards" and option2 == "pob"):
        award = option1_details if option1 == "awards" else option2_details

        if award == "Hall of Fame":
            results = get_players_pob_hof()

        if award == "All Star":
            results = get_players_pob_allStar()

        if award in standard_awards:
            results = get_players_pob_stdAward(award)

    elif (option1 == "dp" and option2 == "awards") or (option1 == "awards" and option2 == "dp"):
        award = option1_details if option1 == "awards" else option2_details
        if award == "Hall of Fame":
            results = get_players_draftPick_hof()
        elif award == "All Star":
            results = get_players_draftPick_allStar()


    elif (option1 == "positions" and option2 == "positions"):
        position1 = option1_details
        position2 = option2_details
        results = get_players_position_position(position1, position2)

    elif (option1 == "pob" and option2 == "positions") or (option1 == "positions" and option2 == "pob"):
        position = option1_details if option1 == "positions" else option2_details
        results = get_players_pob_position(position)

    elif (option1 == "dp" and option2 == "positions") or (option1 == "positions" and option2 == "dp"):
        position = option1_details if option1 == "positions" else option2_details
        results = get_players_draftPick_position(position)



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