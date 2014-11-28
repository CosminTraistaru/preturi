from flask import render_template, redirect, url_for, g
from forms import SearchForm
from app import app, models
from app.config import MAX_SEARCH_RESULTS

@app.route('/<product_id>')
@app.route('/produs/<product_id>')
def produs(product_id):
    produs = {}
    pr = models.Produs().query.get(product_id)
    produs['preturi'] = pr.preturi_dict()
    produs['nume'] = pr.NumeProdus
    produs['link'] = pr.LinkProdus
    produs['image'] = pr.PozaProdus
    produs['magazin'] = pr.Magazin
    return render_template('produs.html', produs=produs,
                           title="Cand imi cumpar {produs} ?".format(
                               produs=pr.NumeProdus
                           ))
@app.before_request
def before_request():
    g.search_form = SearchForm()

@app.route('/search', methods=['POST'])
def search():
    # results = models.Produs.query.whoosh_search("Laptop Apple MacBook Pro 13")
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')
def search_results(query):
    results = models.Produs.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',
                           title="Cand imi cumpar? - Pagina nu exista"), 404