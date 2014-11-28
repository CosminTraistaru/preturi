from app import app, db
import flask.ext.whooshalchemy


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
    idPret = db.Column(db.Integer, autoincrement=True, primary_key=True)
    idProdus = db.Column(db.Integer, db.ForeignKey('produs.idProdus'))
    Pret = db.Column(db.DECIMAL(10, 4))
    Data = db.Column(db.Date)

    def __repr__(self):
        return "{} {}".format(int(self.Pret), self.Data)


class Produs(db.Model):
    __searchable__ = ['NumeProdus']
    __tablename__ = 'produs'

    idProdus = db.Column(db.Integer, autoincrement=True, primary_key=True)
    idCategorie = db.Column(db.Integer, default=0)
    idMagazin = db.Column(db.Integer, db.ForeignKey('magazin.idMagazin'))
    Magazin = db.relationship('Magazin', backref="produs")
    NumeProdus = db.Column(db.Text)
    LinkProdus = db.Column(db.Text)
    PozaProdus = db.Column(db.Text)
    hash = db.Column(db.VARCHAR(40))
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

# Produs.pu
#
# def rebuild_index(model=Produs):
#     """Rebuild search index of Flask-SQLAlchemy model"""
#     primary_field = model.pure_whoosh.primary_key_name
#     searchables = model.__searchable__
#     index_writer = flask.ext.whooshalchemy.whoosh_index(app, model)
#
#     # Fetch all data
#     entries = model.query.all()
#
#     entry_count = 0
#     with index_writer.writer() as writer:
#         for entry in entries:
#             index_attrs = {}
#             for field in searchables:
#                 index_attrs[field] = unicode(getattr(entry, field))
#
#             index_attrs[primary_field] = unicode(getattr(entry, primary_field))
#             writer.update_document(**index_attrs)
#             entry_count += 1