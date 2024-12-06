from app.models import People, Batting, Teams, db, Fielding, Awards, HallOfFame, AllStarFull, Appearances, Pitching, \
    SeriesPost, FieldingPost, BattingPost, ImmaculateGridTeams

from sqlalchemy import func, and_, or_

def get_player_card_info(name):
    player = name.split()
    subquery = (
        db.session.query(
            People.nameFirst,
            People.nameLast,
            Teams.team_name,
            Teams.yearID,
            People.birthCountry,
            People.height,
            People.weight,
            Batting.b_HR,
            Batting.yearID,

        )
        .filter(and_(People.nameFirst == player[0], People.nameLast == player[1]))
        .filter(Batting.playerID == People.playerID)
        .filter(and_(Teams.teamID == Batting.teamID, Teams.yearID == Batting.yearID))
        .all()
    )
    print(subquery)
    return subquery