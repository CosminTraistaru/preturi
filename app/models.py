import threading
import random
import time
import flask.ext.whooshalchemy

from app import app, db


class Categorie(db.Model):
    __tablename__ = 'categorie'
    idCategorie = db.Column(db.Integer, autoincrement=True, primary_key=True)
    NumeCategorie = db.Column(db.Text)


class Magazin(db.Model):
    __tablename__ = 'magazin'
    idMagazin = db.Column(db.Integer, autoincrement=True, primary_key=True)
    Nume = db.Column(db.Text)
    LinkMagazin = db.Column(db.Text)
    Descriere = db.Column(db.Text)

    def __repr__(self):
        return "{magazin} ".format(magazin=self.Nume.title())


class Pret(db.Model):
    __tablename__ = 'pret'
    idProdus = db.Column(db.VARCHAR(40),
                         db.ForeignKey('produs.idProdus'))
    Pret = db.Column(db.DECIMAL(10, 4))
    Data = db.Column(db.Date, primary_key=True)

    def __repr__(self):
        return "{} {}".format(int(self.Pret), self.Data)


class Produs(db.Model):
    __searchable__ = ['NumeProdus']
    __tablename__ = 'produs'

    idProdus = db.Column(db.VARCHAR(40), primary_key=True)
    idCategorie = db.Column(db.Integer, default=0)
    idMagazin = db.Column(db.Integer, db.ForeignKey('magazin.idMagazin'))
    Magazin = db.relationship('Magazin', backref="produs")
    NumeProdus = db.Column(db.Text)
    LinkProdus = db.Column(db.Text)
    PozaProdus = db.Column(db.Text)
    # hash = db.Column(db.VARCHAR(40))
    Preturi = db.relationship('Pret', backref="produs", lazy='dynamic')

    def __str__(self):
        return "Produs: {nume_produs} \nLink Produs: {link_produs}".\
            format(nume_produs=self.NumeProdus, link_produs=self.LinkProdus)

    def preturi_dict(self):
        return [
            {'day': p.Data.strftime("%Y-%m-%d"),
             'value': int(p.Pret)}
            for p in self.Preturi.all()
        ]


def get_product_info(id_prod):
    produs = {}
    pr = Produs().query.get(id_prod)
    # import ipdb;ipdb.set_trace()
    produs['preturi'] = pr.preturi_dict()
    produs['nume'] = pr.NumeProdus
    produs['link'] = pr.LinkProdus
    produs['image'] = pr.PozaProdus
    produs['magazin'] = pr.Magazin
    return produs


def rebuild_index(model):
    """Rebuild search index of Flask-SQLAlchemy model"""
    primary_field = 'idProdus'
    searchables = model.__searchable__
    index_writer = flask.ext.whooshalchemy.whoosh_index(app, model)

    # Fetch all data
    entries = model.query.all()

    entry_count = 0
    with index_writer.writer() as writer:
        for entry in entries:
            index_attrs = {}
            for field in searchables:
                index_attrs[field] = unicode(getattr(entry, field))

            index_attrs[primary_field] = unicode(getattr(entry, primary_field))
            writer.update_document(**index_attrs)
            entry_count += 1
    print "rebuild model complete"

def rebuid_id_index(model):
    entries = model.query.all()
    i = 1
    for entry in entries:
        entry.idProdus = i
        i += 1

class GetSales(object):

    sale = random.randint(10, 30000)
    finished = False

    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        print "starting the timer {}".format(time.time())
        start_time = time.time()
        self.sale = self.biggest_sale(Produs)['id']
        print time.time() - start_time

    def get_bigget_sale(self):
        return self.sale

    @staticmethod
    def process_entry(prod):
        """ a) create a list of the dict's keys and values;
            b) return the key with the max value"""
        dict = prod.preturi_dict()
        max_value = max(dict, key=lambda x: x['value'])
        min_value = min(dict, key=lambda x: x['value'])
        diff = 100 - ((min_value['value'] * 100)/max_value['value'])
        return diff

    def biggest_sale(self, model):
        entries = model.query.all()
        sales_list = [
            {'id': e.idProdus,
             'value': self.process_entry(e)}
            for e in entries
            ]
        return max(sales_list, key=lambda x: x['value'])


# run_in_the_backgroud = GetSales()
# sales = run_in_the_backgroud.get_bigget_sale()
