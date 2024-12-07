from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    # last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class People(db.Model):
    __tablename__ = 'people'
    playerID = db.Column(db.String(9), primary_key=True)
    birthYear = db.Column(db.Integer)
    birthMonth = db.Column(db.Integer)
    birthDay = db.Column(db.Integer)
    birthCountry = db.Column(db.String(255))
    birthState = db.Column(db.String(255))
    birthCity = db.Column(db.String(255))
    deathYear = db.Column(db.Integer)
    deathMonth = db.Column(db.Integer)
    deathDay = db.Column(db.Integer)
    deathCountry = db.Column(db.String(255))
    deathState = db.Column(db.String(255))
    deathCity = db.Column(db.String(255))
    nameFirst = db.Column(db.String(255))
    nameLast = db.Column(db.String(255))
    nameGiven = db.Column(db.String(255))
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    bats = db.Column(db.String(255))
    throws = db.Column(db.String(255))
    debutDate = db.Column(db.Date)
    finalGameDate = db.Column(db.Date)


class Batting(db.Model):
    __tablename__ = 'batting'
    batting_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerID = db.Column(db.String(9), db.ForeignKey('people.playerID'), nullable=False)
    yearID = db.Column(db.SmallInteger, nullable=False)
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


class Teams(db.Model):
    __tablename__ = 'teams'
    teams_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teamID = db.Column(db.String(3), db.ForeignKey('league.teamID'), nullable=False)  # Assuming a League table exists
    yearID = db.Column(db.SmallInteger, nullable=False)
    lgID = db.Column(db.String(2), db.ForeignKey('league.lgID'))  # Assuming you have a League table
    divID = db.Column(db.String(1))
    franchID = db.Column(db.String(3))
    team_name = db.Column(db.String(50))
    team_rank = db.Column(db.SmallInteger)
    team_G = db.Column(db.SmallInteger)
    team_G_home = db.Column(db.SmallInteger)
    team_W = db.Column(db.SmallInteger)
    team_L = db.Column(db.SmallInteger)
    DivWin = db.Column(db.String(1))
    WCWin = db.Column(db.String(1))
    LgWin = db.Column(db.String(1))
    WSWin = db.Column(db.String(1))
    team_R = db.Column(db.SmallInteger)
    team_AB = db.Column(db.SmallInteger)
    team_H = db.Column(db.SmallInteger)
    team_2B = db.Column(db.SmallInteger)
    team_3B = db.Column(db.SmallInteger)
    team_HR = db.Column(db.SmallInteger)
    team_BB = db.Column(db.SmallInteger)
    team_SO = db.Column(db.SmallInteger)
    team_SB = db.Column(db.SmallInteger)
    team_CS = db.Column(db.SmallInteger)
    team_HBP = db.Column(db.SmallInteger)
    team_SF = db.Column(db.SmallInteger)
    team_RA = db.Column(db.SmallInteger)
    team_ER = db.Column(db.SmallInteger)
    team_ERA = db.Column(db.Float)
    team_CG = db.Column(db.SmallInteger)
    team_SHO = db.Column(db.SmallInteger)
    team_SV = db.Column(db.SmallInteger)
    team_IPouts = db.Column(db.Integer)
    team_HA = db.Column(db.SmallInteger)
    team_HRA = db.Column(db.SmallInteger)
    team_BBA = db.Column(db.SmallInteger)
    team_SOA = db.Column(db.SmallInteger)
    team_E = db.Column(db.SmallInteger)
    team_DP = db.Column(db.SmallInteger)
    team_FP = db.Column(db.Float)
    park_name = db.Column(db.String(50))
    team_attendance = db.Column(db.Integer)
    team_BPF = db.Column(db.SmallInteger)
    team_PPF = db.Column(db.SmallInteger)
    team_projW = db.Column(db.SmallInteger)
    team_projL = db.Column(db.SmallInteger)


class Awards(db.Model):
    __tablename__ = 'awards'  # Table name in your database

    awards_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    awardID = db.Column(db.String(255), nullable=False)
    yearID = db.Column(db.SmallInteger, nullable=False)
    playerID = db.Column(db.String(9), db.ForeignKey('people.playerID'), nullable=False)
    lgID = db.Column(db.CHAR(2), nullable=False)
    tie = db.Column(db.String(1))
    notes = db.Column(db.String(100))


class Drafts(db.Model):
    __tablename__ = 'drafts'  # Table name in your database

    draft_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerID = db.Column(db.String(9), db.ForeignKey('people.playerID'), nullable=False)
    yearID = db.Column(db.SmallInteger)
    draft_round = db.Column(db.SmallInteger)
    draft_pick = db.Column(db.SmallInteger)


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


class HallOfFame(db.Model):
    __tablename__ = 'halloffame'

    halloffame_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incremented ID
    playerID = db.Column(db.String(9), db.ForeignKey('people.playerID'), nullable=False)  # Foreign key to People table
    yearID = db.Column(db.SmallInteger, nullable=False)
    votedBy = db.Column(db.String(64), nullable=False)
    ballots = db.Column(db.SmallInteger)
    needed = db.Column(db.SmallInteger)
    votes = db.Column(db.SmallInteger)
    inducted = db.Column(db.String(1))  # 'Y' or 'N'
    category = db.Column(db.String(20))
    note = db.Column(db.String(25))


class AllStarFull(db.Model):
    __tablename__ = 'allstarfull'

    allstarfull_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerID = db.Column(db.String(9), nullable=False, index=True)
    lgID = db.Column(db.CHAR(2), nullable=False, index=True)
    teamID = db.Column(db.CHAR(3), nullable=False)
    yearID = db.Column(db.SmallInteger, nullable=False)
    gameID = db.Column(db.String(12), nullable=True)
    GP = db.Column(db.SmallInteger, nullable=True)
    startingPos = db.Column(db.SmallInteger, nullable=True)


class Appearances(db.Model):
    __tablename__ = 'appearances'

    # Primary key
    appearances_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    playerID = db.Column(db.String(9), db.ForeignKey('people.playerID'), nullable=False)
    teamID = db.Column(db.String(3), db.ForeignKey('teams.teamID'), nullable=False)
    yearID = db.Column(db.SmallInteger, nullable=False)

    # Games Played
    G_all = db.Column(db.SmallInteger)
    GS = db.Column(db.SmallInteger)  # Games started
    G_batting = db.Column(db.SmallInteger)  # Games played as a batter
    G_defense = db.Column(db.SmallInteger)  # Games played in defense
    G_p = db.Column(db.SmallInteger)  # Games played as a pitcher
    G_c = db.Column(db.SmallInteger)  # Games played as a catcher
    G_1b = db.Column(db.SmallInteger)  # Games played at first base
    G_2b = db.Column(db.SmallInteger)  # Games played at second base
    G_3b = db.Column(db.SmallInteger)  # Games played at third base
    G_ss = db.Column(db.SmallInteger)  # Games played at shortstop
    G_lf = db.Column(db.SmallInteger)  # Games played in left field
    G_cf = db.Column(db.SmallInteger)  # Games played in center field
    G_rf = db.Column(db.SmallInteger)  # Games played in right field
    G_of = db.Column(db.SmallInteger)  # Games played in the outfield
    G_dh = db.Column(db.SmallInteger)  # Games played as a designated hitter
    G_ph = db.Column(db.SmallInteger)  # Games played as a pinch hitter
    G_pr = db.Column(db.SmallInteger)  # Games played as a pinch runner


class Pitching(db.Model):
    __tablename__ = 'pitching'

    pitching_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerID = db.Column(db.String(9), nullable=False, index=True)
    yearID = db.Column(db.SmallInteger, nullable=False)
    teamID = db.Column(db.CHAR(3), nullable=False, index=True)
    stint = db.Column(db.SmallInteger, nullable=False)
    p_W = db.Column(db.SmallInteger, nullable=True)
    p_L = db.Column(db.SmallInteger, nullable=True)
    p_G = db.Column(db.SmallInteger, nullable=True)
    p_GS = db.Column(db.SmallInteger, nullable=True)
    p_CG = db.Column(db.SmallInteger, nullable=True)
    p_SHO = db.Column(db.SmallInteger, nullable=True)
    p_SV = db.Column(db.SmallInteger, nullable=True)
    p_IPOuts = db.Column(db.Integer, nullable=True)
    p_H = db.Column(db.SmallInteger, nullable=True)
    p_ER = db.Column(db.SmallInteger, nullable=True)
    p_HR = db.Column(db.SmallInteger, nullable=True)
    p_BB = db.Column(db.SmallInteger, nullable=True)
    p_SO = db.Column(db.SmallInteger, nullable=True)
    p_BAOpp = db.Column(db.Float, nullable=True)
    p_ERA = db.Column(db.Float, nullable=True)
    p_IBB = db.Column(db.SmallInteger, nullable=True)
    p_WP = db.Column(db.SmallInteger, nullable=True)
    p_HBP = db.Column(db.SmallInteger, nullable=True)
    p_BK = db.Column(db.SmallInteger, nullable=True)
    p_BFP = db.Column(db.SmallInteger, nullable=True)
    p_GF = db.Column(db.SmallInteger, nullable=True)
    p_R = db.Column(db.SmallInteger, nullable=True)
    p_SH = db.Column(db.SmallInteger, nullable=True)
    p_SF = db.Column(db.SmallInteger, nullable=True)
    p_GIDP = db.Column(db.SmallInteger, nullable=True)


class SeriesPost(db.Model):
    __tablename__ = 'seriespost'

    seriespost_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teamIDwinner = db.Column(db.CHAR(3), nullable=False, index=True)
    teamIDloser = db.Column(db.CHAR(3), nullable=False, index=True)
    yearID = db.Column(db.SmallInteger, nullable=False)
    round = db.Column(db.String(5), nullable=False)
    wins = db.Column(db.SmallInteger, nullable=True)
    losses = db.Column(db.SmallInteger, nullable=True)
    ties = db.Column(db.SmallInteger, nullable=True)


class FieldingPost(db.Model):
    __tablename__ = 'fieldingpost'

    fieldingpost_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerID = db.Column(db.String(9), nullable=False, index=True)  # Player ID
    yearID = db.Column(db.SmallInteger, nullable=False)  # Year of the postseason
    teamID = db.Column(db.CHAR(3), nullable=False, index=True)  # Team ID
    round = db.Column(db.String(10), nullable=False)  # Postseason round
    position = db.Column(db.String(2), nullable=True)  # Fielding position
    f_G = db.Column(db.SmallInteger, nullable=True)  # Games played
    f_GS = db.Column(db.SmallInteger, nullable=True)  # Games started
    f_InnOuts = db.Column(db.SmallInteger, nullable=True)  # Innings played (outs recorded)
    f_PO = db.Column(db.SmallInteger, nullable=True)  # Putouts
    f_A = db.Column(db.SmallInteger, nullable=True)  # Assists
    f_E = db.Column(db.SmallInteger, nullable=True)  # Errors
    f_DP = db.Column(db.SmallInteger, nullable=True)  # Double plays
    f_TP = db.Column(db.SmallInteger, nullable=True)  # Triple plays
    f_PB = db.Column(db.SmallInteger, nullable=True)  # Passed balls (for catchers)


class BattingPost(db.Model):
    __tablename__ = 'battingpost'

    battingpost_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique ID
    playerID = db.Column(db.String(9), nullable=False, index=True)  # Player ID
    yearId = db.Column(db.SmallInteger, nullable=False)  # Year of the postseason
    teamID = db.Column(db.CHAR(3), nullable=False, index=True)  # Team ID
    round = db.Column(db.String(10), nullable=False)  # Postseason round
    b_G = db.Column(db.SmallInteger, nullable=True)  # Games played
    b_AB = db.Column(db.SmallInteger, nullable=True)  # At-bats
    b_R = db.Column(db.SmallInteger, nullable=True)  # Runs
    b_H = db.Column(db.SmallInteger, nullable=True)  # Hits
    b_2B = db.Column(db.SmallInteger, nullable=True)  # Doubles
    b_3B = db.Column(db.SmallInteger, nullable=True)  # Triples
    b_HR = db.Column(db.SmallInteger, nullable=True)  # Home runs
    b_RBI = db.Column(db.SmallInteger, nullable=True)  # Runs batted in
    b_SB = db.Column(db.SmallInteger, nullable=True)  # Stolen bases
    b_CS = db.Column(db.SmallInteger, nullable=True)  # Caught stealing
    b_BB = db.Column(db.SmallInteger, nullable=True)  # Walks
    b_SO = db.Column(db.SmallInteger, nullable=True)  # Strikeouts
    b_IBB = db.Column(db.SmallInteger, nullable=True)  # Intentional walks
    b_HBP = db.Column(db.SmallInteger, nullable=True)  # Hit by pitch
    b_SH = db.Column(db.SmallInteger, nullable=True)  # Sacrifice hits
    b_SF = db.Column(db.SmallInteger, nullable=True)  # Sacrifice flies
    b_GIDP = db.Column(db.SmallInteger, nullable=True)  # Grounded into double plays


class AdvancedStats(db.Model):
    __tablename__ = 'advanced_stats'

    advanced_stats_ID = db.Column(db.BigInteger, primary_key=True)
    playerID = db.Column(db.Text, nullable=True)
    yearID = db.Column(db.BigInteger, nullable=True)
    teamID = db.Column(db.Text, nullable=True)
    stint = db.Column(db.BigInteger, nullable=True)
    is_P = db.Column(db.Text, nullable=True)
    sched = db.Column(db.BigInteger, nullable=True)
    g_bat = db.Column(db.BigInteger, nullable=True)
    pa = db.Column(db.BigInteger, nullable=True)
    bat162 = db.Column(db.Float, nullable=True)
    bsr162 = db.Column(db.Float, nullable=True)
    fld162 = db.Column(db.Float, nullable=True)
    pos162 = db.Column(db.Float, nullable=True)
    def162 = db.Column(db.Float, nullable=True)
    rep162 = db.Column(db.Float, nullable=True)
    bwar162 = db.Column(db.Float, nullable=True)
    BB_plus = db.Column(db.Float, nullable=True)
    K_plus = db.Column(db.Float, nullable=True)
    AVG_plus = db.Column(db.Float, nullable=True)
    OBP_plus = db.Column(db.Float, nullable=True)
    SLG_plus = db.Column(db.Float, nullable=True)
    wRC_plus = db.Column(db.Float, nullable=True)
    ISO_plus = db.Column(db.Float, nullable=True)
    BABIP_plus = db.Column(db.Float, nullable=True)
    LD_plus = db.Column(db.Float, nullable=True)
    GB_plus = db.Column(db.Float, nullable=True)
    FB_plus = db.Column(db.Float, nullable=True)
    Pull_plus = db.Column(db.Float, nullable=True)
    Cent_plus = db.Column(db.Float, nullable=True)
    Oppo_plus = db.Column(db.Float, nullable=True)
    g_pitch = db.Column(db.Float, nullable=True)
    starts = db.Column(db.Float, nullable=True)
    innings = db.Column(db.Float, nullable=True)
    relief_pct = db.Column(db.Float, nullable=True)
    avg_LI = db.Column(db.Float, nullable=True)
    br_pwar162 = db.Column(db.Float, nullable=True)
    fg_pwar162 = db.Column(db.Float, nullable=True)
    ra9_pwar162 = db.Column(db.Float, nullable=True)
    pwar162 = db.Column(db.Float, nullable=True)
    K9_plus = db.Column(db.Float, nullable=True)
    BB9_plus = db.Column(db.Float, nullable=True)
    KBB_plus = db.Column(db.Float, nullable=True)
    HR9_plus = db.Column(db.Float, nullable=True)
    Kpct_plus = db.Column(db.Float, nullable=True)
    BBpct_plus = db.Column(db.Float, nullable=True)
    oppAVG_plus = db.Column(db.Float, nullable=True)
    WHIP_plus = db.Column(db.Float, nullable=True)
    oppBABIP_plus = db.Column(db.Float, nullable=True)
    LOB_plus = db.Column(db.Float, nullable=True)
    ERA_minus = db.Column(db.Float, nullable=True)
    FIP_minus = db.Column(db.Float, nullable=True)
    xFIP_minus = db.Column(db.Float, nullable=True)
    oppLD_plus = db.Column(db.Float, nullable=True)
    oppGB_plus = db.Column(db.Float, nullable=True)
    oppFB_plus = db.Column(db.Float, nullable=True)
    pct_PT = db.Column(db.Float, nullable=True)
    WAR162 = db.Column(db.Float, nullable=True)
    gms_P = db.Column(db.Float, nullable=True)
    gms_C = db.Column(db.Float, nullable=True)
    gms_1B = db.Column(db.Float, nullable=True)
    gms_2B = db.Column(db.Float, nullable=True)
    gms_3B = db.Column(db.Float, nullable=True)
    gms_SS = db.Column(db.Float, nullable=True)
    gms_LF = db.Column(db.Float, nullable=True)
    gms_CF = db.Column(db.Float, nullable=True)
    gms_RF = db.Column(db.Float, nullable=True)
    gms_OF = db.Column(db.Float, nullable=True)
    gms_DH = db.Column(db.Float, nullable=True)
    gms_PH = db.Column(db.Float, nullable=True)
    gms_PR = db.Column(db.Float, nullable=True)
    prev_tm = db.Column(db.Text, nullable=True)
    arrived = db.Column(db.BigInteger, nullable=True)
    departed = db.Column(db.BigInteger, nullable=True)
    next_tm = db.Column(db.Text, nullable=True)
    salary = db.Column(db.Float, nullable=True)


class LeagueStats(db.Model):
    __tablename__ = 'league_stats'

    league_stats_id = db.Column(db.BigInteger, primary_key=True)
    yearID = db.Column(db.SmallInteger, nullable=False)
    TG = db.Column(db.BigInteger, nullable=True)
    W = db.Column(db.BigInteger, nullable=True)
    L = db.Column(db.BigInteger, nullable=True)
    G = db.Column(db.BigInteger, nullable=True)
    PA = db.Column(db.BigInteger, nullable=True)
    HR = db.Column(db.BigInteger, nullable=True)
    R = db.Column(db.BigInteger, nullable=True)
    RBI = db.Column(db.BigInteger, nullable=True)
    SB = db.Column(db.Double, nullable=True)
    BB_percent = db.Column(db.Text, nullable=True)
    K_percent = db.Column(db.Text, nullable=True)
    ISO = db.Column(db.Double, nullable=True)
    BABIP = db.Column(db.Double, nullable=True)
    AVG = db.Column(db.Double, nullable=True)
    OBP = db.Column(db.Double, nullable=True)
    SLG = db.Column(db.Double, nullable=True)
    wOBA = db.Column(db.Double, nullable=True)
    wOBA_scale = db.Column(db.Double, nullable=True)
    GDP = db.Column(db.BigInteger, nullable=True)
    xwOBA = db.Column(db.Double, nullable=True)
    wRC_plus = db.Column(db.BigInteger, nullable=True)
    BsR = db.Column(db.Double, nullable=True)
    Off = db.Column(db.Double, nullable=True)
    Def = db.Column(db.Double, nullable=True)
    WAR = db.Column(db.Double, nullable=True)
    IP = db.Column(db.Double, nullable=True)
    runSB = db.Column(db.Double, nullable=True)
    runCS = db.Column(db.Double, nullable=True)
    b_1B = db.Column(db.BigInteger, nullable=True)
    b_2B = db.Column(db.BigInteger, nullable=True)
    b_3B = db.Column(db.BigInteger, nullable=True)
    BB = db.Column(db.BigInteger, nullable=True)
    IBB = db.Column(db.Double, nullable=True)
    HBP = db.Column(db.Double, nullable=True)
    CS = db.Column(db.Double, nullable=True)
    AB = db.Column(db.BigInteger, nullable=True)
    SO = db.Column(db.BigInteger, nullable=True)
    SF = db.Column(db.BigInteger, nullable=True)
    wBB = db.Column(db.Double, nullable=True)
    wHBP = db.Column(db.Double, nullable=True)
    w1B = db.Column(db.Double, nullable=True)
    w2B = db.Column(db.Double, nullable=True)
    w3B = db.Column(db.Double, nullable=True)
    wHR = db.Column(db.Double, nullable=True)


class ImmaculateGridTeams(db.Model):
    __tablename__ = 'immaculategridteams'

    ig_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ig_team_name = db.Column(db.String(50), nullable=False)
    team_name = db.Column(db.String(50), nullable=False)
    startYear = db.Column(db.SmallInteger, nullable=False)
    endYear = db.Column(db.SmallInteger, nullable=False)
