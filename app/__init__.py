#!flask/bin/python

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
AppConfig(app)
Bootstrap(app)
app.config['SECRET_KEY'] = 'devkey'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://preturi:preturi@localhost/preturi'
db = SQLAlchemy(app)
