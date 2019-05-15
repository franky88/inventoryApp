from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail
from inventory.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    from inventory.users.routes import users
    from inventory.posts.routes import posts
    from inventory.main.routes import main
    from inventory.api.routes import api
    from inventory.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(errors)

    return app