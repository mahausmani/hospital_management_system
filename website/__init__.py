from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from flask_user import UserManager

db = SQLAlchemy()
db_name = "database.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "hello world"
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{db_name}'
    app.config['USER_ENABLE_EMAIL'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .view import view
    from .model import User
    app.register_blueprint(view, url_prefix='/')
    # if not path.exists('website/' + db_name):
    #     db.create_all(app=app)

    @app.before_request
    def create_tables():
        db.create_all()

    login_manager = LoginManager()
    # user_manager = UserManager(app, db, User)
    login_manager.login_view = 'view.home'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
