from flask import render_template

from app import app
from app import models


@app.route('/')
@app.route('/index')
def index():
    produs = {}
    pr = models.Produs()
    produs['preturi'], produs['nume'], produs['link'], produs['image'] = \
        pr.get_product()
    return render_template('index.html', produs=produs)
