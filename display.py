import simplejson as json

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import Form
from flask_bootstrap import WebCDN

import database


def retrieve_product():
    connection = database.connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM produs WHERE produs.idProdus = 250;")
    result = cursor.fetchall()
    nume = result[0][3]
    link = result[0][4]
    image = result[0][5]
    cursor.execute("SELECT * from pret WHERE pret.idProdus = 250;")
    result = cursor.fetchall()
    preturi = [({'day': str(pret[3]), 'value': str(int(pret[2]))})
               for pret in result]
    json_response = json.dumps(preturi)
    database.disconnect_db(connection)
    return preturi, nume, link, image, json_response


class Produs(Form):
    magazin = 'emag'
    preturi, nume, link, image, json_response = retrieve_product()


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)
    Bootstrap(app)
    app.config['SECRET_KEY'] = 'devkey'
    app.config['RECAPTCHA_PUBLIC_KEY'] = \
        '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'
    app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
        '//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/'
    )

    @app.route('/')
    @app.route('/index')
    def index():
        produs = Produs()
        return render_template('index.html', produs=produs)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
