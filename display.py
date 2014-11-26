from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_bootstrap import WebCDN

import database


class Produs():
    def __init__(self):
        pass

    @staticmethod
    def get_product(product_id=250):
            connection = database.connect_db()
            cursor = connection.cursor()
            cursor.execute("""SELECT * FROM produs WHERE produs.idProdus = %s;""", (product_id,))
            result = cursor.fetchall()
            nume = result[0][3]
            link = result[0][4]
            image = result[0][5]
            cursor.execute("""SELECT * from pret WHERE pret.idProdus = %s;""", (product_id,))
            result = cursor.fetchall()
            preturi = [({'day': str(pret[3]), 'value': str(int(pret[2]))})
                       for pret in result]
            database.disconnect_db(connection)
            return preturi, nume, link, image


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
        produs = {}
        pr = Produs()
        produs['preturi'], \
        produs['nume'], \
        produs['link'], \
        produs['image'] = pr.get_product()
        return render_template('index.html', produs=produs)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
