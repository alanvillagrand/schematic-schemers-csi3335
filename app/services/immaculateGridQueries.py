from app.models import People, Batting, Teams, db, Fielding, Awards, HallOfFame, AllStarFull, Appearances, Pitching, \
    SeriesPost, FieldingPost, BattingPost, Drafts, AdvancedStats, ImmaculateGridTeams, CareerWar, SeasonWar

from sqlalchemy import func, and_, or_

''' Subquery Functions '''
def join_subqueries(subquery1, subquery2):
    main_query = (
        db.session.query(subquery1, subquery2)
        .join(subquery1, subquery1.c.playerID == subquery2.c.playerID)
        .subquery()
    )
    # Get Name and sort by total game appearances
    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(main_query, main_query.c.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == main_query.c.playerID)
        .group_by(Appearances.playerID)
        .order_by(db.func.sum(Appearances.G_all))
        .all()
    )

def played_on_team_subquery(option_details):
    subquery = (
        db.session.query(
            Appearances.playerID, Appearances.yearID, Appearances.teamID
        )
        .join(Teams, and_(Teams.teamID == Appearances.teamID, Teams.yearID == Appearances.yearID))
        .join(ImmaculateGridTeams, ImmaculateGridTeams.team_name == Teams.team_name)
        .filter(ImmaculateGridTeams.ig_team_name == option_details)
        .filter(Teams.yearID >= ImmaculateGridTeams.startYear)
        .filter(or_(ImmaculateGridTeams.endYear.is_(None), Teams.yearID <= ImmaculateGridTeams.endYear))
        .subquery()
    )
    return subquery


""" Teams Queries"""

""" 
get_players_team_team
Queries a player that played for two different teams
Takes in the two teams as parameters
Algorithm uses the appearances table to get players with the least total appearances
"""


def get_players_team_team(option1_details, option2_details):
    team_subquery1 = played_on_team_subquery(option1_details)
    team_subquery2 = played_on_team_subquery(option2_details)
    # Join Subqueries
    return join_subqueries(team_subquery1, team_subquery2)


"""
get_players_seasonStatBatting_team
queries for a player that has this batting stat and achieved it in a season with the team
takes in a team, stat, and stat_range
algorithm orders it by least appearances in batting b_G
"""

def get_players_seasonStatBatting_team(stat, team, stat_range):
    batting_column1 = getattr(Batting, f"b_{stat}")

    team_subquery = played_on_team_subquery(team)
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(team_subquery, and_(
            team_subquery.c.playerID == Batting.playerID,
            team_subquery.c.teamID == Batting.teamID,
        ))
        .filter(batting_column1 >= stat_range)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonStatBatting_onlyOneTeam(stat, stat_range):
    batting_column1 = getattr(Batting, f"b_{stat}")

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(batting_column1 >= stat_range)
        .filter(Batting.playerID.in_(
            db.session.query(Batting.playerID)
            .group_by(Batting.playerID)
            .having(db.func.count(db.distinct(Batting.teamID)) == 1)
        ))  # Inline subquery with select()
        .order_by(db.func.sum(Batting.b_G).asc())
        .all()
    )

def get_players_position_onlyOneTeam(position):
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'

    # Subquery to get players who have played for only one team
    subquery = (
        db.session.query(Appearances.playerID)
        .group_by(Appearances.playerID)
        .having(db.func.count(db.distinct(Appearances.teamID)) == 1)
    )

    # Main query for players who meet the position condition and are in the subquery
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(getattr(Appearances, position_column) > 0)
        .filter(Appearances.playerID.in_(subquery))  # Filter by players with one team
        .order_by(db.func.sum(getattr(Appearances, position_column)).asc())
        .all()
    )


def get_players_seasonBattingAVG_onlyOneTeam(stat_range):

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H / Batting.b_AB) >= stat_range)
        .filter(Batting.playerID.in_(
            db.session.query(Batting.playerID)
            .group_by(Batting.playerID)
            .having(db.func.count(db.distinct(Batting.teamID)) == 1)
        ))  # Inline subquery with select()
        .order_by(db.func.sum(Batting.b_G).asc())
        .all()
    )


def get_players_seasonBatting3030_onlyOneTeam():

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .filter(Batting.playerID.in_(
            db.session.query(Batting.playerID)
            .group_by(Batting.playerID)
            .having(db.func.count(db.distinct(Batting.teamID)) == 1)
        ))  # Inline subquery with select()
        .order_by(db.func.sum(Batting.b_G).asc())
        .all()
    )


def get_players_seasonStatPitching_onlyOneTeam(stat, stat_range):
    pitching_column1 = getattr(Pitching, f"p_{stat}")

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(pitching_column1 >= stat_range)
        .filter(Pitching.playerID.in_(
            db.session.query(Pitching.playerID)
            .group_by(Pitching.playerID)
            .having(db.func.count(db.distinct(Pitching.teamID)) == 1)
        ))  # Inline subquery with select()
        .order_by(db.func.sum(Pitching.p_G).asc())
        .all()
    )


def get_players_seasonPitchingERA_onlyOneTeam():

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(Pitching.p_ERA <= 3.00)
        .filter(Pitching.playerID.in_(
            db.session.query(Pitching.playerID)
            .group_by(Pitching.playerID)
            .having(db.func.count(db.distinct(Pitching.teamID)) == 1)
        ))  # Inline subquery with select()
        .order_by(db.func.sum(Pitching.p_G).asc())
        .all()
    )

def get_players_ws_team(team):
    team_subquery = played_on_team_subquery(team)
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(team_subquery, team_subquery.c.playerID == People.playerID)
        .join(SeriesPost, SeriesPost.teamIDwinner == team_subquery.c.teamID)
        .filter(SeriesPost.round == 'WS')
        .filter(Teams.yearID == SeriesPost.yearID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()

    )

"""fix this"""
def get_players_seasonStatWAR_team(team, stat_range):

    team_subquery = played_on_team_subquery(team)
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(team_subquery, and_(
            team_subquery.c.playerID == Appearances.playerID,
            team_subquery.c.teamID == Appearances.teamID,
        ))
        .join(SeasonWar, SeasonWar.playerID == team_subquery.c.playerID)
        .filter(SeasonWar.war >= stat_range)
        .filter(SeasonWar.yearID == Appearances.yearID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )


def get_players_careerStatWAR_team(team, stat_range):

    team_subquery = played_on_team_subquery(team)
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(CareerWar, CareerWar.playerID == People.playerID)
        .join(team_subquery, team_subquery.c.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(CareerWar.war >= stat_range)
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )


def get_players_careerStatWAR_onlyOneTeam(stat_range):

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(CareerWar, CareerWar.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(CareerWar.war >= stat_range)
        .group_by(People.playerID)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )


def get_players_seasonPitchingERA_team(team):

    team_subquery = played_on_team_subquery(team)
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(team_subquery, and_(
            team_subquery.c.playerID == Pitching.playerID,
            team_subquery.c.teamID == Pitching.teamID,
        ))
        .filter(Pitching.p_ERA <= 3.00)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonStatPitching_team(stat_column, team, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")

    team_subquery = played_on_team_subquery(team)
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(team_subquery, and_(
            team_subquery.c.playerID == Pitching.playerID,
            team_subquery.c.teamID == Pitching.teamID,
        ))
        .filter(pitching_column >= stat_range)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


def get_players_hof_team(team):
    team_subquery = played_on_team_subquery(team)

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .join(team_subquery, team_subquery.c.playerID == HallOfFame.playerID)
        .filter(HallOfFame.inducted == 'Y')
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )



def get_players_pob_team(team):
    team_subquery = played_on_team_subquery(team)

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(team_subquery, team_subquery.c.playerID == People.playerID)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )


def get_players_pob_onlyOneTeam():

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )

def get_players_country_onlyOneTeam(country):

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )

def get_players_country_team(team, country):
    team_subquery = played_on_team_subquery(team)

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(team_subquery, team_subquery.c.playerID == People.playerID)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )


def get_players_position_team(position, team):
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'

    team_subquery = played_on_team_subquery(team)
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(team_subquery, and_(
            team_subquery.c.playerID == Appearances.playerID,
            team_subquery.c.teamID == Appearances.teamID,
        ))
        .filter(getattr(Appearances, position_column) > 0)
        .group_by(People.playerID)
        .order_by(db.func.sum(getattr(Appearances, position_column)).asc())
        .distinct()
        .all()
    )




def get_players_seasonBattingAVG_team(stat_range, team):
    team_subquery = played_on_team_subquery(team)
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(team_subquery, and_(
            team_subquery.c.playerID == Batting.playerID,
            team_subquery.c.teamID == Batting.teamID,
        ))
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H / Batting.b_AB) >= stat_range)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )



def get_players_exclusive_to_team(team):
    team_subquery = played_on_team_subquery(team)
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .join(team_subquery, team_subquery.c.playerID == People.playerID)
        .group_by(People.playerID)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )


def get_players_hof_onlyOneTeam():

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(HallOfFame.inducted == 'Y')
        .group_by(People.playerID)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )


def get_players_stdAward_onlyOneTeam(award):

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(Awards.awardID == award)
        .group_by(People.playerID)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .distinct()
        .all()
    )


def get_players_allStar_onlyOneTeam():

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(AllStarFull.GP > 0)
        .group_by(People.playerID)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(AllStarFull.GP).asc())
        .distinct()
        .all()
    )


"""
get_players_seasonBatting3030_team
queries for a player that has this 3030 and achieved it in a season
while playing for the specific team
takes in a team
algorithm orders it by least appearances in batting b_G
"""


def get_players_seasonBatting3030_team(team):
    team_subquery = played_on_team_subquery(team)
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(team_subquery, team_subquery.c.playerID == Batting.playerID)
        .filter(Batting.b_SB > 30)
        .filter(Batting.b_HR > 30)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )


"""
get_players_careerStatBatting_team
Queries a player that achieved a batting stat over their entire career and played at least one game with the team.
Takes in a team, the stat_column, and the stat range.
Algorithm uses the batting table to calculate career totals and orders by least total appearances (b_G).
"""


def get_players_careerStatBatting_team(stat_column, team, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    total_stat = db.func.sum(batting_column).label("total_stat")

    team_subquery = played_on_team_subquery(team)

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
        .join(team_subquery, team_subquery.c.playerID == Batting.playerID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )


def get_players_careerStatBatting_onlyOneTeam(stat_column, stat_range):
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
        .join(Teams, Teams.teamID == Batting.teamID)
        .group_by(People.playerID)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )


def get_players_careerStatPitching_onlyOneTeam(stat_column, stat_range):
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
        .join(Teams, Teams.teamID == Pitching.teamID)
        .group_by(People.playerID)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


"""
get_players_careerStatPitching_team
Queries a player that achieved a pitching stat over their career and played at least one game with the team.
Takes in a team, the stat_column, and the stat range.
Algorithm uses the pitching table to calculate career totals and orders by least total appearances (p_G).
"""


def get_players_careerStatPitching_team(stat_column, team, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    total_stat = db.func.sum(pitching_column).label("total_stat")

    team_subquery = played_on_team_subquery(team)

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
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(team_subquery, team_subquery.c.playerID == Pitching.playerID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )

def get_players_careerPitchingERA_team(team):

    team_subquery = played_on_team_subquery(team)

    career_stats = (
        db.session.query(
            Pitching.playerID
        )

        .group_by(Pitching.playerID)
        .having(func.sum(Pitching.p_IPOuts > 0))
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(team_subquery, team_subquery.c.playerID == Pitching.playerID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


def get_players_careerPitchingERA_onlyOneTeam():

    career_stats = (
        db.session.query(
            Pitching.playerID
        )

        .group_by(Pitching.playerID)
        .having(func.sum(Pitching.p_IPOuts > 0))
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Teams, Teams.teamID == Pitching.teamID)
        .group_by(People.playerID)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


"""
get_players_careerBattingAVG_team
Queries a player that achieved this average stat over their career and played at least one game with the team.
Takes in the stat_column, and team
Algorithm uses the batting table to calculate career totals and orders by least total appearances (b_G).
"""


def get_players_careerBattingAVG_team(stat_range, team):
    team_subquery = played_on_team_subquery(team)

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(Batting, Batting.playerID == People.playerID)
        .join(team_subquery, team_subquery.c.playerID == People.playerID)
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)
        .order_by(db.func.sum(Batting.b_G).asc())
        .all()
    )



def get_players_careerBattingAVG_onlyOneTeam(stat_range):

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(Batting, Batting.playerID == People.playerID)
        .join(Teams, Teams.teamID == Batting.teamID)
        .group_by(People.playerID)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)
        .having(db.func.count(db.func.distinct(Teams.teamID)) == 1)
        .order_by(db.func.sum(Batting.b_G).asc())
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
    return (
        db.session.query(
            People.nameFirst,
            People.nameLast,
        )
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, and_(Teams.teamID == Appearances.teamID, Teams.yearID == Appearances.yearID))
        .join(ImmaculateGridTeams, ImmaculateGridTeams.team_name == Teams.team_name)
        .join(Awards, and_(Awards.yearID == Teams.yearID, Awards.playerID == Appearances.playerID))
        .filter(ImmaculateGridTeams.ig_team_name == team)
        .filter(Teams.yearID >= ImmaculateGridTeams.startYear)
        .filter(or_(ImmaculateGridTeams.endYear.is_(None), Teams.yearID <= ImmaculateGridTeams.endYear))
        .filter(Awards.awardID == stdAward)
        .order_by(db.func.sum(Appearances.G_all))
        .group_by(Appearances.playerID)
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
        .join(Teams, and_(Teams.teamID == AllStarFull.teamID, Teams.yearID == AllStarFull.yearID))
        .join(ImmaculateGridTeams, ImmaculateGridTeams.team_name == Teams.team_name)
        .filter(ImmaculateGridTeams.ig_team_name == team)
        .filter(Teams.yearID >= ImmaculateGridTeams.startYear)
        .filter(or_(ImmaculateGridTeams.endYear.is_(None), Teams.yearID <= ImmaculateGridTeams.endYear))
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

def get_players_stdAward_position(award, position):
    position_column = f'G_{position.lower()}'
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)  # Join to check position
        .join(Awards, Awards.playerID == People.playerID)  # Check All-Star appearances
        .filter(
            getattr(Appearances, position_column) > 0,  # Played the specified position
            Awards.awardID == award
        )
        .group_by(People.playerID)
        .order_by(db.func.sum(getattr(Appearances, position_column)).asc())
        .distinct()
        .all()
    )

def get_players_hof_position(position):
    position_column = f'G_{position.lower()}'
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)  # Join to check position
        .join(HallOfFame, HallOfFame.playerID == People.playerID)  # Check All-Star appearances
        .filter(
            getattr(Appearances, position_column) > 0,  # Played the specified position
            HallOfFame.inducted == "Y"
        )
        .group_by(People.playerID)
        .order_by(db.func.sum(getattr(Appearances, position_column)).asc())
        .distinct()
        .all()
    )

def get_players_allstar_position(position):
    position_column = f'G_{position.lower()}'
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)  # Check All-Star appearances
        .filter(
            getattr(Appearances, position_column) > 0,  # Played the specified position
            AllStarFull.GP > 0
        )
        .group_by(People.playerID)
        .order_by(db.func.sum(AllStarFull.GP).asc())
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
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(awards_query, awards_query.c.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .group_by(People.playerID, People.nameFirst, People.nameLast)  # Group by player to get the sum of appearances
        .having(func.sum(Appearances.G_all).isnot(None))  # Ensure that the player has appearances
        .order_by(func.sum(Appearances.G_all).asc())  # Order by total appearances in ascending order
        .all()
    )


def get_players_hof_stdAward(award):
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Awards, Awards.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(Awards.awardID == award)
        .filter(HallOfFame.inducted == "Y")
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
        .all()
    )

def get_players_allStar_stdAward(award):
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Awards, Awards.playerID == People.playerID)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .filter(Awards.awardID == award)
        .filter(AllStarFull.GP > 0)
        .group_by(People.playerID)
        .order_by(db.func.sum(AllStarFull.GP).asc())
        .all()
    )



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

def get_players_country_position(position, country):
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(
            People.birthCountry == country, getattr(Appearances, position_column) > 0 )
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

def get_players_country_hof(country):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .filter(People.birthCountry == country)
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


def get_players_country_allStar(country):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .filter(People.birthCountry == country)
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


def get_players_country_stdAward(award, country):
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(People.birthCountry == country)
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


def get_players_seasonBattingAVG_stdAward(stat_range, award):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .filter(Batting.b_AB > 0)
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


def get_players_seasonBatting3030_hof():
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .filter(HallOfFame.inducted == 'Y')
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )


def get_players_seasonBatting3030_allStar():
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .filter(AllStarFull.GP > 0)
        .group_by(People.playerID)
        .order_by(db.func.sum(AllStarFull.GP).asc())
        .distinct()
        .all()
    )

def get_players_seasonBattingAVG_allStar(stat_range):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .filter(Batting.b_AB > 0)
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
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H/ Batting.b_AB) >= stat_range)  # Batting average of .300 or higher
        .filter(HallOfFame.inducted == 'Y')
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonWAR_hof(stat_range):
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .join(AdvancedStats, AdvancedStats.playerID == People.playerID)
        .filter(AdvancedStats.WAR162 >= stat_range)
        .filter(HallOfFame.inducted == 'Y')
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonWAR_position(stat_range, position):
    position_column = f'G_{position.lower()}'

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(AdvancedStats, AdvancedStats.playerID == People.playerID)
        .filter(AdvancedStats.bwar162 >= stat_range)
        .filter(getattr(Appearances, position_column) > 0)
        .group_by(People.playerID)
        .order_by(func.sum(getattr(Appearances, position_column)))
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


def get_players_seasonStatBatting3030_seasonStatPitching(pitching_column, pitching_range):
    pitching_column1 = getattr(Pitching, f"p_{pitching_column}")
    pitching_subquery = (
        db.session.query(Pitching.playerID)
        .filter(pitching_column1 >= pitching_range)
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
        .join(pitching_subquery, pitching_subquery.c.playerID == People.playerID)
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

def get_players_seasonStatERA_allStar():
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .filter(Pitching.p_ERA <= 3.00)
        .group_by(People.playerID)  # Group by player to ensure distinct results
        .order_by(db.func.sum(AllStarFull.GP).asc())
        .distinct()
        .all()
    )

def get_players_seasonStatERA_hof():
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .filter(
            Pitching.p_ERA <= 3.00,
            HallOfFame.inducted == 'Y'
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

def get_players_seasonStatPitching_position(stat_column, position, stat_range):
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'
    pitching_column = getattr(Pitching, f"p_{stat_column}")

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(
            pitching_column >= stat_range, getattr(Appearances, position_column) > 0 )
        .group_by(People.playerID)  # Group by player ID to calculate total appearances
        .order_by(func.sum(getattr(Appearances, position_column)))
        .distinct()
        .all()
    )

def get_players_seasonPitchingERA_position(position):
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(
            Pitching.p_ERA <= 3.00, getattr(Appearances, position_column) > 0 )
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
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H/Batting.b_AB) >= stat_range)
        .filter(getattr(Appearances, position_column) > 0 )
        .group_by(People.playerID)  # Group by player ID to calculate total appearances
        .order_by(func.sum(getattr(Appearances, position_column)))
        .distinct()
        .all()
    )

def get_players_seasonBatting3030_position(position):
    # Construct the column name for the specified position (e.g., G_ss, G_1b)
    position_column = f'G_{position.lower()}'

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Teams, Teams.teamID == Appearances.teamID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .filter(getattr(Appearances, position_column) > 0 )
        .group_by(People.playerID)  # Group by player ID to calculate total appearances
        .order_by(func.sum(getattr(Appearances, position_column)))
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

def get_players_seasonStatBatting_country(stat_column, stat_range, country):
    batting_column = getattr(Batting, f"b_{stat_column}")

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(batting_column >= stat_range)
        .filter(People.birthCountry == country)
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

def get_players_seasonStatPitching_country(stat_column, stat_range, country):
    pitching_column = getattr(Pitching, f"p_{stat_column}")

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(pitching_column >= stat_range)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonPitchingERA_pob():

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(Pitching.p_ERA <= 3.00)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonPitchingERA_country(country):

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(Pitching.p_ERA <= 3.00)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


def get_players_seasonBattingAVG_pob(stat_range):

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H / Batting.b_AB) >= stat_range)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonBattingAVG_country(stat_range, country):

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H / Batting.b_AB) >= stat_range)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )


def get_players_seasonBatting3030_pob():

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )

def get_players_seasonBatting3030_country(country):

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
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

def get_players_allStar_hof():
    return(
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .join(HallOfFame, HallOfFame.playerID == People.playerID)
        .filter(HallOfFame.inducted == 'Y')
        .filter(AllStarFull.GP > 0)
        .group_by(People.playerID)
        .order_by(db.func.sum(AllStarFull.GP).asc())
        .distinct()
        .all()
    )

def get_players_careerPitchingERA_hof():
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
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(People.playerID.in_(db.select(in_hof.c.playerID)))  # Filter only players from the subquery
        .group_by(People.playerID)
        .having(func.sum(Pitching.p_IPOuts) > 0)
        .having((func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00)
        .order_by(db.func.sum(Pitching.p_G).asc())  # Order by least games played
        .distinct()
        .all()
    )

def get_players_careerPitchingERA_allStar():
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
        .join(AllStarFull, AllStarFull.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(People.playerID.in_(db.select(in_allStar.c.playerID)))  # Filter only players from the subquery
        .group_by(People.playerID)
        .having(func.sum(Pitching.p_IPOuts) > 0)
        .having((func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00)
        .order_by(db.func.sum(AllStarFull.GP).asc())  # Order by least games played
        .distinct()
        .all()
    )

def get_players_careerPitchingERA_stdAward(award):
    in_stdAward = (
        db.session.query(Awards.playerID)
        .filter(Awards.awardID == award)
        .group_by(Awards.playerID)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast  # Only select first and last name
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(People.playerID.in_(db.select(in_stdAward.c.playerID)))  # Filter only players from the subquery
        .group_by(People.playerID)
        .having(func.sum(Pitching.p_IPOuts) > 0)
        .having((func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00)
        .order_by(db.func.sum(Pitching.p_G).asc())  # Order by least games played
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


def get_players_careerStatPitching_position(stat_column, stat_range, position):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    total_stat = db.func.sum(pitching_column).label('total_stat')
    position_column = f'G_{position.lower()}'

    career_stats= (
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

def get_players_careerPitchingERA_position(position):
    position_column = f'G_{position.lower()}'
    plays_position = (
        db.session.query(Appearances.playerID)
        .filter(getattr(Appearances, position_column) > 0)
        .group_by(Appearances.playerID)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast  # Only select first and last name
        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(People.playerID.in_(db.select(plays_position.c.playerID)))  # Filter only players from the subquery
        .group_by(People.playerID)
        .having(func.sum(Pitching.p_IPOuts) > 0)
        .having((func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00)
        .order_by(db.func.sum(getattr(Appearances, position_column)).asc())
        .distinct()
        .all()
    )

def get_players_careerStatPitching_pob(stat_column, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    total_stat = db.func.sum(pitching_column).label('total_stat')

    career_stats= (
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
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()

    )


def get_players_careerStatPitching_country(stat_column, stat_range, country):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    total_stat = db.func.sum(pitching_column).label('total_stat')

    career_stats= (
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
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()

    )

def get_players_careerStatBatting_pob(stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    total_stat = db.func.sum(batting_column).label('total_stat')

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
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()

    )



def get_players_careerStatBatting_country(stat_column, stat_range, country):
    batting_column = getattr(Batting, f"b_{stat_column}")
    total_stat = db.func.sum(batting_column).label('total_stat')

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
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()

    )


def get_players_careerBattingAVG_pob(stat_range):

    career_stats= (
        db.session.query(
            Batting.playerID
        )
        .group_by(Batting.playerID)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()

    )


def get_players_careerBattingAVG_country(stat_range, country):

    career_stats= (
        db.session.query(
            Batting.playerID
        )
        .group_by(Batting.playerID)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()

    )

def get_players_careerPitchingERA_pob():

    career_stats= (
        db.session.query(
            Pitching.playerID
        )
        .filter(Pitching.p_IPOuts > 0)
        .group_by(Pitching.playerID)
        .having(func.sum(Pitching.p_IPOuts) > 0)
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()

    )


def get_players_careerPitchingERA_country(country):

    career_stats= (
        db.session.query(
            Pitching.playerID
        )
        .filter(Pitching.p_IPOuts > 0)
        .group_by(Pitching.playerID)
        .having(func.sum(Pitching.p_IPOuts) > 0)
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()

    )



def get_players_careerStatBatting_draftPick(stat_column, stat_range):
    batting_column = getattr(Batting, f"b_{stat_column}")
    total_stat = db.func.sum(batting_column).label('total_stat')

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
        .join(Batting, Batting.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()

    )

def get_players_careerBattingAVG_draftPick(stat_range):

    career_stats= (
        db.session.query(
            Batting.playerID,
        )
        .group_by(Batting.playerID)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()

    )


def get_players_careerStatPitching_draftPick(stat_column, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")
    total_stat = db.func.sum(pitching_column).label('total_stat')

    career_stats= (
        db.session.query(
            Pitching.playerID
        )
        .group_by(Pitching.playerID)
        .having(total_stat > stat_range)
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()

    )



def get_players_careerPitchingERA_draftPick():

    career_stats= (
        db.session.query(
            Pitching.playerID
        )
        .group_by(Pitching.playerID)
        .having(db.func.sum(Pitching.p_IPOuts) > 0)
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )
        .subquery()
    )

    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(career_stats, career_stats.c.playerID == People.playerID)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
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
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .distinct()
        .all()
    )


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
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
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

def get_players_careerStatPitching_careerStatPitching(stat_column1, stat_range1, stat_column2, stat_range2):
    pitching_column1 = getattr(Pitching, f"p_{stat_column1}")
    pitching_column2 = getattr(Pitching, f"p_{stat_column2}")

    # Subqueries to check for each stat independently
    stat1_subquery = (
        db.session.query(Pitching.playerID)
        .group_by(Pitching.playerID)
        .having(db.func.sum(pitching_column1) >= stat_range1)
        .subquery()
    )
    stat2_subquery = (
        db.session.query(Pitching.playerID)
        .group_by(Pitching.playerID)
        .having(db.func.sum(pitching_column2) >= stat_range2)
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

def get_players_careerBattingAVG_careerStatPitching(avg_range, stat_column, stat_range):
    pitching_column = getattr(Pitching, f"p_{stat_column}")

    # Subqueries to check for each stat independently
    stat1_subquery = (
        db.session.query(Pitching.playerID)
        .group_by(Pitching.playerID)
        .having(db.func.sum(pitching_column) >= stat_range)
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
        .filter(Batting.b_AB > 0)
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

def get_players_seasonPitchingERA_seasonStatPitching(pitching_column, pitching_range):
    pitching_column1 = getattr(Pitching, f"p_{pitching_column}")
    pitching_subquery = (
        db.session.query(Pitching.playerID)
        .filter(pitching_column1 >= pitching_range)
        .subquery()
    )
    era_subquery = (
        db.session.query(Pitching.playerID)
        .filter(Pitching.p_ERA <= 3.00)
        .subquery()

    )

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(pitching_subquery, pitching_subquery.c.playerID == People.playerID)
        .join(era_subquery, era_subquery.c.playerID == People.playerID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


def get_players_seasonPitchingERA_seasonStatBatting(batting_column, batting_range):
    batting_column1 = getattr(Batting, f"b_{batting_column}")
    batting_subquery = (
        db.session.query(Batting.playerID)
        .filter(batting_column1 >= batting_range)
        .subquery()
    )
    era_subquery = (
        db.session.query(Pitching.playerID)
        .filter(Pitching.p_ERA <= 3.00)
        .subquery()

    )

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(batting_subquery, batting_subquery.c.playerID == People.playerID)
        .join(era_subquery, era_subquery.c.playerID == People.playerID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
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
        .filter(Batting.b_AB > 0)
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


def get_players_seasonBatting3030_seasonStatAVG(avg_range):
    batting_subquery = (
        db.session.query(Batting.playerID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .subquery()
    )
    avg_subquery = (
        db.session.query(Batting.playerID)
        .filter(Batting.b_AB > 0)
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

def get_players_seasonPitchingERA_seasonStatAVG(avg_range):
    pitching_subquery = (
        db.session.query(Pitching.playerID)
        .filter(Pitching.p_ERA <= 3.00)
        .subquery()
    )
    avg_subquery = (
        db.session.query(Batting.playerID)
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H/Batting.b_AB) >= avg_range)
        .subquery()

    )

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(pitching_subquery, pitching_subquery.c.playerID == People.playerID)
        .join(avg_subquery, avg_subquery.c.playerID == People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
        .group_by(People.playerID)
        .distinct()
        .all()
    )


def get_players_seasonPitchingERA_seasonBatting3030():
    pitching_subquery = (
        db.session.query(Pitching.playerID)
        .filter(Pitching.p_ERA <= 3.00)
        .subquery()
    )
    batting_subquery = (
        db.session.query(Batting.playerID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .subquery()

    )

    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(pitching_subquery, pitching_subquery.c.playerID == People.playerID)
        .join(batting_subquery, batting_subquery.c.playerID == People.playerID)
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


def get_players_careerStatBatting_seasonPitchingERA(career_column, career_range):
    career_column1 = getattr(Batting, f"b_{career_column}")

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
            Pitching.playerID
        )
        .filter(Pitching.p_ERA <= 3.00)  # Per-season filter
        .group_by(Pitching.playerID)
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



def get_players_careerStatPitching_seasonPitchingERA(career_column, career_range):
    career_column1 = getattr(Pitching, f"p_{career_column}")

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
        .filter(Pitching.p_ERA <= 3.00)  # Per-season filter
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


def get_players_careerStatBatting_seasonStatPitching(career_column, career_range, season_column, season_range):
    career_column1 = getattr(Batting, f"b_{career_column}")
    season_column1 = getattr(Pitching, f"p_{season_column}")

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
            Pitching.playerID
        )
        .filter(season_column1 >= season_range)  # Per-season filter
        .group_by(Pitching.playerID)
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

def get_players_careerStatPitching_seasonStatBatting(career_column, career_range, season_column, season_range):
    career_column1 = getattr(Pitching, f"p_{career_column}")
    season_column1 = getattr(Batting, f"b_{season_column}")

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

def get_players_careerPitchingERA_seasonStatPitching(season_column, season_range):
    season_column1 = getattr(Pitching, f"p_{season_column}")

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Pitching.playerID)  # Group stats by player
        .having(func.sum(Pitching.p_IPOuts) > 0)
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Pitching.playerID
        )
        .filter(season_column1 >= season_range)
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


def get_players_careerPitchingERA_seasonStatBatting(season_column, season_range):
    season_column1 = getattr(Batting, f"b_{season_column}")

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Pitching.playerID)  # Group stats by player
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter(season_column1 >= season_range)
        .group_by(Batting.playerID)
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


def get_players_careerPitchingERA_seasonPitchingERA():

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Pitching.playerID)  # Group stats by player
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Pitching.playerID
        )
        .filter(Pitching.p_ERA <= 3.00)
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



def get_players_careerPitchingERA_seasonStatAVG(season_range):

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Pitching.playerID)  # Group stats by player
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H/ Batting.b_AB) >= season_range)
        .group_by(Batting.playerID)
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


def get_players_careerPitchingERA_seasonBatting3030():

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Pitching.playerID)  # Group stats by player
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .group_by(Batting.playerID)
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



def get_players_careerPitchingERA_careerStatPitching(career_column, career_range):
    career_column1 = getattr(Pitching, f"p_{career_column}")

    # Subquery for career stats
    era_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Pitching.playerID)  # Group stats by player
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    career_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Pitching.playerID)  # Group stats by player
        .having(
            db.func.sum(career_column1) >= career_range
        )  # Weighted ERA <= 3.00
        .subquery()
    )


    # Main query to find players matching both criteria
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(career_subquery, career_subquery.c.playerID == People.playerID)
        .join(era_subquery, era_subquery.c.playerID == People.playerID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )

def get_players_careerPitchingERA_careerStatBatting(career_column, career_range):
    career_column1 = getattr(Batting, f"b_{career_column}")

    # Subquery for career stats
    era_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Pitching.playerID)  # Group stats by player
        .having(func.sum(Pitching.p_IPOuts) > 0)
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    career_subquery = (
        db.session.query(
            Batting.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Batting.playerID)  # Group stats by player
        .having(
            db.func.sum(career_column1) >= career_range
        )  # Weighted ERA <= 3.00
        .subquery()
    )


    # Main query to find players matching both criteria
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(career_subquery, career_subquery.c.playerID == People.playerID)
        .join(era_subquery, era_subquery.c.playerID == People.playerID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


def get_players_careerPitchingERA_careerStatAVG(career_range):

    # Subquery for career stats
    era_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .filter(Pitching.p_IPOUTS > 0)
        .group_by(Pitching.playerID)  # Group stats by player
        .having(func.sum(Pitching.p_IPOuts) > 0)
        .having(
            (func.sum(Pitching.p_ER) / (func.sum(Pitching.p_IPOuts) / 3)) * 9 <= 3.00
        )  # Weighted ERA <= 3.00
        .subquery()
    )

    career_subquery = (
        db.session.query(
            Batting.playerID  # Only return player IDs that meet the criteria
        )

        .group_by(Batting.playerID)  # Group stats by player
        .having(db.func.sum(Batting.b_AB) > 0)
        .having(
            ((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= career_range)
        )  # Weighted ERA <= 3.00
        .subquery()
    )


    # Main query to find players matching both criteria
    return (
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(career_subquery, career_subquery.c.playerID == People.playerID)
        .join(era_subquery, era_subquery.c.playerID == People.playerID)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
        .distinct()
        .all()
    )


def get_players_careerBattingAVG_seasonStatBatting(season_column, season_range, career_range):
    season_column1 = getattr(Batting, f"b_{season_column}")

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Batting.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Batting.playerID)  # Group stats by player
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H)/ db.func.sum(Batting.b_AB)) >= career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter(season_column1 >= season_range)
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


def get_players_careerBattingAVG_seasonBatting3030(career_range):

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Batting.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Batting.playerID)  # Group stats by player
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H)/ db.func.sum(Batting.b_AB)) >= career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
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


def get_players_careerBattingAVG_seasonBattingAVG(career_range, season_range):

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Batting.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Batting.playerID)  # Group stats by player
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H)/ db.func.sum(Batting.b_AB)) >= career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter((Batting.b_H/Batting.b_AB) >= season_range)
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


def get_players_careerBattingAVG_seasonPitchingERA(career_range):

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Batting.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Batting.playerID)  # Group stats by player
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H)/ db.func.sum(Batting.b_AB)) >= career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Pitching.playerID
        )
        .filter(Pitching.p_ERA <= 3.00)
        .group_by(Pitching.playerID)
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



def get_players_careerBattingAVG_seasonStatPitching(season_column, season_range, career_range):
    season_column1 = getattr(Pitching, f"p_{season_column}")

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Batting.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Batting.playerID)  # Group stats by player
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H)/ db.func.sum(Batting.b_AB)) >= career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Pitching.playerID
        )
        .filter(season_column1 >= season_range)
        .group_by(Pitching.playerID)
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


def get_players_careerStatBatting_seasonBattingAVG(career_column, career_range, season_range):
    career_column1 = getattr(Batting, f"b_{career_column}")

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Batting.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Batting.playerID)  # Group stats by player
        .having(db.func.sum(career_column1) > career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H /Batting.b_AB) >= season_range)
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


def get_players_careerStatPitching_seasonBattingAVG(career_column, career_range, season_range):
    career_column1 = getattr(Pitching, f"p_{career_column}")

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Pitching.playerID)  # Group stats by player
        .having(db.func.sum(career_column1) > career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H /Batting.b_AB) >= season_range)
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

def get_players_careerStatBatting_seasonBatting3030(career_column, career_range):
    career_column1 = getattr(Batting, f"b_{career_column}")

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Batting.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Batting.playerID)  # Group stats by player
        .having(db.func.sum(career_column1) > career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
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

def get_players_careerStatPitching_seasonBatting3030(career_column, career_range):
    career_column1 = getattr(Pitching, f"p_{career_column}")

    # Subquery for career stats
    career_subquery = (
        db.session.query(
            Pitching.playerID  # Only return player IDs that meet the criteria
        )
        .group_by(Pitching.playerID)  # Group stats by player
        .having(db.func.sum(career_column1) > career_range)
        .subquery()
    )

    # Subquery for season stats
    season_subquery = (
        db.session.query(
            Batting.playerID
        )
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
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

def get_players_draftPick_stdAward(award):
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Appearances, Appearances.playerID == People.playerID)
        .join(Awards, Awards.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(Awards.awardID == award)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
    )

def get_players_draftPick_seasonStatPitching(season_column, season_range):
    season_column1 = getattr(Pitching, f"p_{season_column}")
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(season_column1 >= season_range)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
    )

def get_players_draftPick_seasonPitchingERA():
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(Pitching.p_ERA <= 3.00)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Pitching.p_G).asc())
    )

def get_players_draftPick_seasonStatBatting(season_column, season_range):
    season_column1 = getattr(Batting, f"b_{season_column}")
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(season_column1 >= season_range)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
    )

def get_players_draftPick_seasonBattingAVG(season_range):
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(Batting.b_AB > 0)
        .filter((Batting.b_H / Batting.b_AB) >= season_range)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
    )

def get_players_draftPick_seasonBatting3030():
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Batting, Batting.playerID == People.playerID)
        .join(Drafts, Drafts.playerID == People.playerID)
        .filter(Batting.b_SB >= 30)
        .filter(Batting.b_HR >= 30)
        .filter(Drafts.draft_round == 1)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
    )

def get_players_draftPick_pob():
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Drafts, Drafts.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(Drafts.draft_round == 1)
        .filter(People.birthCountry != "USA")
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
    )


def get_players_draftPick_country(country):
    return(
        db.session.query(People.nameFirst, People.nameLast)
        .join(Drafts, Drafts.playerID == People.playerID)
        .join(Appearances, Appearances.playerID == People.playerID)
        .filter(Drafts.draft_round == 1)
        .filter(People.birthCountry == country)
        .group_by(People.playerID)
        .order_by(db.func.sum(Appearances.G_all).asc())
    )