from flask import Blueprint, request, session, redirect, url_for, render_template
from app.models import User, db

bp = Blueprint('auth', __name__)

@bp.route("/login", methods=["POST"])
def login():
    print("IN LOGIN")
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        print("Here")
        session['username'] = username
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', error="Invalid username or password")


@bp.route("/register", methods=["POST"])
def register():
    print("IN REGISTER")
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("index.html", error="Username already registered")
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    session['username'] = username
    return redirect(url_for('main.dashboard'))


@bp.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('main.home'))
