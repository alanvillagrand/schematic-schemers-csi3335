from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.secret_key = "secret"

    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:csi3335rocks@localhost/baseball'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register blueprints
    from app.routes import auth_routes, main_routes, search_routes, team_routes
    app.register_blueprint(auth_routes)
    app.register_blueprint(main_routes)
    app.register_blueprint(search_routes)
    app.register_blueprint(team_routes)

    return app
