from app.models import Teams, Batting, People, Pitching
from sqlalchemy import func, literal, desc
from sqlalchemy.sql import text
from datetime import datetime
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
    date = datetime.strptime(year + "-06-30", "%Y-%m-%d")
    results = (
        db.session.query(
            func.concat(People.nameFirst, ' ', People.nameLast),
            (func.extract('year', date) - People.birthYear).label('age'),
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
            func.round(calculate_wOBA(), 3),
            0, # wRC+
            0, # BsR
            0, # Off
            0, # Def
            0 # WAR
        )
        .join(Batting, Batting.playerID == People.playerID)
        .join(Teams, (Batting.teamID == Teams.teamID) & (Batting.yearID == Teams.yearID))
        .filter(Teams.team_name == team_name, Batting.yearID == year)
        .order_by(desc(Batting.b_G))
        .all()
    )
    return results

# Inning pitched
def calculate_IP():
    return Pitching.p_IPOuts / 3

# Walk rate
def calculate_BB_percentage_pitching():
    return (Pitching.p_BB / Pitching.p_BFP) * 100

# Strikeout rate
def calculate_K_percentage_pitching():
    return (Pitching.p_SO / Pitching.p_BFP) * 100

# Home runs allowed per 9 innings
def calculate_HR9():
    return 9 * Pitching.p_HR / calculate_IP()

# Batting average on balls in play
def calculate_BABIP_pitching():
    # Not sure if this is corect. Using BFP instead of AB since AB isn't in pitching table.
    return (Pitching.p_H - Pitching.p_HR) / (Pitching.p_BFP- Pitching.p_SO - Pitching.p_HR + Pitching.p_SF)

# Left on Base Percentage
def calculate_LOB_percentage():
    return ((Pitching.p_H + Pitching.p_BB + Pitching.p_HBP - Pitching.p_R) / (Pitching.p_H + Pitching.p_BB + Pitching.p_HBP - (1.4*Pitching.p_HR))) * 100

# Fielding Independent Pitching
def calculate_FIP():
    # FIP constant is around 3.10 apparently
    constant = 3.10
    return ((13*Pitching.p_HR) + (3*(Pitching.p_BB + Pitching.p_HBP)) - (2*Pitching.p_SO)) / calculate_IP() + constant

def get_pitching_info(team_name, year):
    date = datetime.strptime(year + "-06-30", "%Y-%m-%d")
    results = (
        db.session.query(
            func.concat(People.nameFirst, ' ', People.nameLast),
            (func.extract('year', date) - People.birthYear).label('age'),
            Pitching.p_G,
            func.round(calculate_IP(), 1),
            func.concat(func.round(calculate_K_percentage_pitching(), 1), literal('%')),
            func.concat(func.round(calculate_BB_percentage_pitching(), 1), literal('%')),
            func.round(calculate_HR9(), 2),
            func.round(calculate_BABIP_pitching(), 3),
            func.concat(func.round(calculate_LOB_percentage(), 1), literal('%')),
            0, # GB%
            0, # HR/FB
            Pitching.p_ERA,
            func.round(calculate_FIP(), 2),
            0, # xFIP
            0 # WAR

        )
        .join(Pitching, Pitching.playerID == People.playerID)
        .join(Teams, (Pitching.teamID == Teams.teamID) & (Pitching.yearID == Teams.yearID))
        .filter(Teams.team_name == team_name, Pitching.yearID == year)
        .all()
    )
    return results