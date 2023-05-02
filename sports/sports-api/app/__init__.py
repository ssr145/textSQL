from app.config import FlaskAppConfig, DB_MANAGED_METADATA
from app.extensions import db
from app.setup.admin_routes import admin_bp
from app.sql_generation.generation_routes import bp as sql_gen_bp
from app.visualization.routes import bp as visualization_bp
from app.games.games_routes import games_bp
from flask import Flask
from flask_admin import Admin
from flask_cors import CORS


def create_app(config_object=FlaskAppConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)
    CORS(app)

    # Initialize app with extensions
    db.init_app(app)
    admin = Admin(None, name='admin', template_mode='bootstrap3')
    admin.init_app(app)

    @app.route("/ping")
    def ping():
        return 'pong'

    app.register_blueprint(sql_gen_bp)
    app.register_blueprint(visualization_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # from app.errors import bp as errors_bp
    # app.register_blueprint(errors_bp)

    # from app.main import bp as main_bp
    # app.register_blueprint(main_bp)

    @app.teardown_request
    def session_clear(exception=None):
        db.session.remove()
        if exception:
            if db.session.is_active:
                db.session.rollback()

    return app
