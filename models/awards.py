from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Awards(db.Model):
    __tablename__ = 'awards'  # Table name in your database

    awards_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    awardID = db.Column(db.String(255), nullable=False)
    yearID = db.Column(db.SmallInteger, nullable=False)
    playerID = db.Column(db.String(9), db.ForeignKey('people.playerID'), nullable=False)
    lgID = db.Column(db.CHAR(2), nullable=False)
    tie = db.Column(db.String(1))
    notes = db.Column(db.String(100))