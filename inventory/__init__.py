import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

BASEDIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = "27bf6b331d1d57a03d6153d7baf58a2a"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASEDIR, 'inventory.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from inventory import routes