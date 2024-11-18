from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Batting(db.Model):
    __tablename__ = 'batting'  # Table name in your database

    batting_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerID = db.Column(db.String(9), db.ForeignKey('people.playerID'), nullable=False)
    yearId = db.Column(db.SmallInteger, nullable=False)
    teamID = db.Column(db.String(3), db.ForeignKey('teams.teamID'), nullable=False)
    stint = db.Column(db.SmallInteger, nullable=False)
    b_G = db.Column(db.SmallInteger)
    b_AB = db.Column(db.SmallInteger)
    b_R = db.Column(db.SmallInteger)
    b_H = db.Column(db.SmallInteger)
    b_2B = db.Column(db.SmallInteger)
    b_3B = db.Column(db.SmallInteger)
    b_HR = db.Column(db.SmallInteger)
    b_RBI = db.Column(db.SmallInteger)
    b_SB = db.Column(db.SmallInteger)
    b_CS = db.Column(db.SmallInteger)
    b_BB = db.Column(db.SmallInteger)
    b_SO = db.Column(db.SmallInteger)
    b_IBB = db.Column(db.SmallInteger)
    b_HBP = db.Column(db.SmallInteger)
    b_SH = db.Column(db.SmallInteger)
    b_SF = db.Column(db.SmallInteger)
    b_GIDP = db.Column(db.SmallInteger)