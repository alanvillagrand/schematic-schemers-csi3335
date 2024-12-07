from flask import Blueprint, request, session, redirect, url_for, render_template
from app.models import User, db

bp = Blueprint('auth', __name__)

@bp.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    print(f"Attempted Username: {username}")
    print(f"Attempted Password: {password}")  # Debugging

    user = User.query.filter_by(username=username).first()

    if user:
        print(f"User found: {user.username}")
        print(f"Stored Hash: {user.password_hash}")
        print(f"Password Check Result: {user.check_password(password)}")

    if user and user.check_password(password):
        session['username'] = username

        if username == 'admin':
            return redirect(url_for('auth.admin_home'))
        return redirect(url_for('main.dashboard'))
    else:
        return render_template('index.html', error="Invalid username or password")


@bp.route("/register", methods=["POST"])
def register():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user:
        return render_template("index.html", error="Username already registered")

    new_user = User(username=username)
    new_user.set_password(password)

    print(f"Plaintext Password: {password}")
    print(f"Generated Hash: {new_user.password_hash}")

    db.session.add(new_user)
    db.session.commit()

    session['username'] = username
    if username == 'admin':
        return redirect(url_for('auth.admin_home'))
    return redirect(url_for('main.dashboard'))


@bp.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('main.home'))


@bp.route("/ban_user/<int:user_id>", methods=["POST"])
def ban_user(user_id):
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('auth.login'))

    user_to_ban = User.query.get(user_id)
    if user_to_ban:
        db.session.delete(user_to_ban)
        db.session.commit()

    return redirect(url_for('auth.admin_home'))


@bp.route("/admin_home")
def admin_home():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('auth.login'))

    users = User.query.all()

    return render_template("admin_home.html", users=users)
