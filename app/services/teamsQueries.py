
"""
from app.models import People, Batting, Teams, db, Fielding, Awards, HallOfFame, AllStarFull, Appearances, Pitching, \
    SeriesPost, FieldingPost, BattingPost

from sqlalchemy import func

""" Teams Queries"""


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
get_players_seasonStatBatting_team
queries for a player that has this batting stat and achieved it in a season with the team
takes in a team, stat, and stat_range
algorithm orders it by least appearances in batting b_G
"""
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


"""
get_players_seasonStatPitching_team
queries for a player that has this pitching stat and achieved it in a season with the team
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
        .filter((Batting.b_H/ Batting.b_AB) >= stat_range)
        .filter(Teams.team_name == team)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
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
    return (
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
get_players_careerStatBatting_team
Queries a player that achieved a batting stat over their entire career and played at least one game with the team.
Takes in a team, the stat_column, and the stat range.
Algorithm uses the batting table to calculate career totals and orders by least total appearances (b_G).
"""
def get_players_careerStatBatting_team(stat_column, team, stat_range):
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
        .filter(Teams.team_name == team)
        .group_by(People.playerID)
        .order_by(db.func.sum(Batting.b_G).asc())
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
        .filter(Teams.team_name == team)
        .group_by(People.playerID)
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
    played_for_team = (
        db.session.query(Batting.playerID)
        .join(Teams, Teams.teamID == Batting.teamID)
        .filter(Teams.team_name == team)
        .group_by(Batting.playerID)
        .subquery()
    )


    return (
        db.session.query(
            People.nameFirst,
            People.nameLast
        )
        .join(Batting, Batting.playerID == People.playerID)
        .filter(People.playerID.in_(played_for_team))
        .group_by(People.playerID, People.nameFirst, People.nameLast)
        .having(db.func.sum(Batting.b_AB) > 0)
        .having((db.func.sum(Batting.b_H) / db.func.sum(Batting.b_AB)) >= stat_range)
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

""" currently not working"""
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


"""Fix this"""
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







