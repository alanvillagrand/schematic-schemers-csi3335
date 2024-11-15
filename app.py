from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret"

#Configure SQL Alchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Ninja123!@localhost/baseball'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Database Model
class User(db.Model):
    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

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


class Teams(db.Model):
    __tablename__ = 'teams'  # The name of the table in your database

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



#Routes
@app.route('/')
def home():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

#Login
@app.route("/login", methods=["POST"])
def login():
    #Collect info from the form
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html', error="Invalid username or password")

#Register
@app.route("/register", methods=["POST"])
def register():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("index.html", error="Username already registered")
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for('dashboard'))


#Dashboard
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session['username'])
    return redirect(url_for('home'))


@app.route('/search_players', methods=['POST'])
def search_players():
    # Extract dropdown values
    option1 = request.form.get('option1')
    option1_details = request.form.get('dropdown1_details')
    option2 = request.form.get('option2')
    option2_details = request.form.get('dropdown2_details')

    # Validate input
    if not option1 or not option2:
        return "Please select an option from both dropdowns.", 400

    results = []

    # Handle search logic based on selected options
    if option1 == "teams" and option2 == "teams":
        # Query players who played on both selected teams
        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(Batting, Batting.playerID == People.playerID)
            .join(Teams, Teams.teamID == Batting.teamID)
            .filter(Teams.team_name.in_([option1_details, option2_details]))
            .group_by(People.playerID, People.nameFirst, People.nameLast)
            .having(db.func.count(Teams.team_name.distinct()) == 2)
            .all()
        )
    elif (option1 == "career statistics" and option2 == "teams") or (option2 == "career statistics" and option1 == "career statistics"):

        # Example: Query career statistics
        # You may need to refine this based on the exact statistics you want to display
        if option1 == "career statistics":
            stat = option1_details
        else:
            stat = option2_details

        # Mock query: Replace this with actual stat-based query logic
        results = (
            db.session.query(People.nameFirst, People.nameLast, Batting.stat_column)
            .filter(Batting.stat_column >= stat)  # Replace `stat_column` with actual stat field
            .all()
        )
    else:
        return "Invalid selection or combination. Please try again.", 400
        # Render results
        # Render results

    if results:
        return render_template('results.html', results=results)
    else:
        return render_template(
            'results.html',
            results=[],
            message="No matching results found for your query."
        )


#Logout
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)