from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Fielding(db.Model):
    __tablename__ = 'fielding'  # Table name in your database

    fielding_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerID = db.Column(db.String(9), db.ForeignKey('people.playerID'), nullable=False)
    yearID = db.Column(db.SmallInteger, nullable=False)
    teamID = db.Column(db.String(3), db.ForeignKey('teams.teamID'), nullable=False)
    stint = db.Column(db.SmallInteger, nullable=False)
    position = db.Column(db.String(2), nullable=True)  # Position (e.g., SS, 2B)
    f_G = db.Column(db.SmallInteger, nullable=True)  # Games
    f_GS = db.Column(db.SmallInteger, nullable=True)  # Games Started
    f_InnOuts = db.Column(db.SmallInteger, nullable=True)  # Innings Outs (1 out = 1/3 inning)
    f_PO = db.Column(db.SmallInteger, nullable=True)  # Putouts
    f_A = db.Column(db.SmallInteger, nullable=True)  # Assists
    f_E = db.Column(db.SmallInteger, nullable=True)  # Errors
    f_DP = db.Column(db.SmallInteger, nullable=True)  # Double Plays
    f_PB = db.Column(db.SmallInteger, nullable=True)  # Passed Balls (Catchers)
    f_WP = db.Column(db.SmallInteger, nullable=True)  # Wild Pitches (Catchers)
    f_SB = db.Column(db.SmallInteger, nullable=True)  # Stolen Bases Allowed
    f_CS = db.Column(db.SmallInteger, nullable=True)  # Caught Stealing
    f_ZR = db.Column(db.Float, nullable=True)  # Zone Rating (defensive metric)
