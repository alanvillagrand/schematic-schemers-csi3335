from app.models import Teams, Batting, People
from sqlalchemy import func, literal, desc
from sqlalchemy.sql import text
from datetime import date
from app import db

# Calculations are taken form fangraphs.com and baseball-reference.com

# Plate appearances
def calculate_PA():
    return Batting.b_AB + Batting.b_BB + Batting.b_HBP + Batting.b_SF + Batting.b_SH

# Walk rate
def calculate_BB_percentage():
    return (Batting.b_BB / calculate_PA()) * 100

# Strikeout rate
def calculate_K_percentage():
    return (Batting.b_SO / calculate_PA()) * 100

# Isolated power
def calcualte_ISO():
    return ((Batting.b_2B) + (2*Batting.b_3B) + (3*Batting.b_HR)) / Batting.b_AB

# Batting average on balls in play
def calculate_BABIP():
    return (Batting.b_H - Batting.b_HR) / (Batting.b_AB - Batting.b_SO - Batting.b_HR + Batting.b_SF)

# Batting average
def calculate_AVG():
    return Batting.b_H / Batting.b_AB

# On-Base percentage
def calculate_OBP():
    return (Batting.b_H + Batting.b_BB + Batting.b_HBP) / (Batting.b_AB + Batting.b_BB + Batting.b_HBP + Batting.b_SF)

# Calculate singles since our database doesn't have this
def calculate_1B():
    return Batting.b_H - (Batting.b_2B + Batting.b_3B + Batting.b_HR)

# Slugging percentage
def calculate_SLG():
    return (calculate_1B() + 2*Batting.b_2B + 3*Batting.b_3B + 4*Batting.b_HR) / Batting.b_AB

# Weighted on-base average
# I'm assuming that BB-IBB is the same as uBB
def calculate_wOBA():
    return (.69*(Batting.b_BB - Batting.b_IBB) + .72*Batting.b_HBP + .89*calculate_1B() + 1.27*Batting.b_2B + 1.62*Batting.b_3B + 2.10*Batting.b_HR) \
    / (Batting.b_AB + Batting.b_BB - Batting.b_IBB + Batting.b_SF + Batting.b_HBP)

def get_team_info(team_name, year):
    return Teams.query.filter_by(team_name=team_name, yearID=year).first()

def get_batting_info(team_name, year):
    current_date = date.today()
    results = (
        db.session.query(
            func.concat(People.nameFirst, ' ', People.nameLast),
            (func.extract('year', current_date) - People.birthYear).label('age'),
            Batting.b_G,
            calculate_PA(),
            Batting.b_HR,
            Batting.b_SB,
            func.concat(func.round(calculate_BB_percentage(), 1), literal('%')),
            func.concat(func.round(calculate_K_percentage(), 1), literal('%')),
            func.round(calcualte_ISO(), 3),
            func.round(calculate_BABIP(), 3),
            func.round(calculate_AVG(), 3),
            func.round(calculate_OBP(), 3),
            func.round(calculate_SLG(), 3),
            func.round(calculate_wOBA(), 3)
        )
        .join(Batting, Batting.playerID == People.playerID)
        .join(Teams, (Batting.teamID == Teams.teamID) & (Batting.yearID == Teams.yearID))
        .filter(Teams.team_name == team_name, Batting.yearID == year)
        .order_by(desc(Batting.b_G))
        .all()
    )
    return results