from app.models import Teams, Batting, People
from sqlalchemy import func
from sqlalchemy.sql import text
from app import db

def get_team_info(team_name, year):
    return Teams.query.filter_by(team_name=team_name, yearID=year).first()

def get_batting_info(team_name, year):
    # Not sure if this query is correct
    query = text("""
        SELECT 
            CONCAT(p.nameFirst, ' ', p.nameLast) AS full_name,
            b.b_G,
            b.b_HR,
            b.b_SB
        FROM people p
        NATURAL JOIN batting b
        NATURAL JOIN teams t
        WHERE t.team_name = :team_name AND t.yearID = :year
    """)
    result = db.session.execute(query, {'team_name': team_name, 'year': year})
    return result.fetchall()