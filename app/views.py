from flask import render_template, redirect, url_for, g, request
from forms import SearchForm
from app import app, models
from app.config import MAX_SEARCH_RESULTS



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


@app.route('/')
def index():
    return render_template('index.html', title="Home")

@app.before_request
def before_request():
    g.search_form = SearchForm()


@app.route('/search', methods=['POST', 'GET'], )
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/')
def search_results():
    query = request.args['srch-term']
    product_list = []
    results = models.Produs.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    no_of_results = len(results)
    for result in results:
        produs = {}
        produs['nume'] = result.NumeProdus
        produs['link'] = result.LinkProdus
        produs['image'] = result.PozaProdus
        produs['magazin'] = result.Magazin
        produs['id'] = result.idProdus
        product_list.append(produs)
    return render_template('search_results.html',
                           no_of_results=no_of_results,
                           query=query,
                           results=product_list,
                           title="Rezultate cautare '{termen}'".format(
                               termen=query))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',
                           title="Cand imi cumpar? - Pagina nu exista"), 404