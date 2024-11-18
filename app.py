from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

from models.awards import Awards
from models.batting import Batting
from models.fielding import Fielding
from models.people import People
from models.teams import Teams
from models.user import User

app = Flask(__name__)
app.secret_key = "secret"

#Configure SQL Alchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Ninja123!@localhost/baseball'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)




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
    elif (option1 == "awards" and option2 == "teams") or (option1 == "teams" and option2 == "awards"):
        # Extract the award and team details
        award = option1_details if option1 == "awards" else option2_details
        team = option1_details if option1 == "teams" else option2_details

        # Query players who played for the team and received the award
        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(Batting, Batting.playerID == People.playerID)
            .join(Teams, Teams.teamID == Batting.teamID)
            .join(Awards, Awards.playerID == People.playerID)
            .filter(Teams.team_name == team, Awards.awardID == award, Awards.yearID == Batting.yearId)
            .distinct()
            .all()
        )
    elif (option1 == "positions" and option2 == "teams") or (option1 == "teams" and option2 == "positions"):
        # Extract the position and team details
        position = option1_details if option1 == "positions" else option2_details
        team = option1_details if option1 == "teams" else option2_details

        # Query players who played in the given position for the selected team
        results = (
            db.session.query(People.nameFirst, People.nameLast)
            .join(Fielding, Fielding.playerID == People.playerID)
            .join(Teams, Teams.teamID == Fielding.teamID)
            .filter(Fielding.position == position, Teams.team_name == team, Fielding.f_G >= 1)  # Played at least 1 game
            .distinct()
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