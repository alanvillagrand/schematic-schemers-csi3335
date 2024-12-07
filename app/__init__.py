from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import csi3335f2024 as cfg

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.secret_key = "secret"

    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = (f'mysql+pymysql://{cfg.mysql["user"]}:{cfg.mysql["password"]}@'
                                             f'{cfg.mysql["host"]}/{cfg.mysql["database"]}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register blueprints
    from app.routes import auth_routes, main_routes, search_routes, team_routes, card_routes
    app.register_blueprint(auth_routes)
    app.register_blueprint(main_routes)
    app.register_blueprint(search_routes)
    app.register_blueprint(team_routes)
    app.register_blueprint(card_routes)

    return app
