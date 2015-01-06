#!flask/bin/python


import flask.ext.whooshalchemy

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask.ext.sqlalchemy import SQLAlchemy

from app.config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, WHOOSH_BASE


app = Flask(__name__)
AppConfig(app)
Bootstrap(app)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['WHOOSH_BASE'] = WHOOSH_BASE
db = SQLAlchemy(app)

from app import views, models
flask.ext.whooshalchemy.whoosh_index(app, models.Produs)
# models.rebuild_index(models.Produs)
# models.rebuid_id_index(models.Produs)