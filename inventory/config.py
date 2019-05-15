import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = "27bf6b331d1d57a03d6153d7baf58a2a"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'inventory.db')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_ADD') #'hubecomputer@gmail.com'# os.environ.get('EMAIL_ADD')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS') #'Hub3T3ch'# os.environ.get('EMAIL_PASS')
