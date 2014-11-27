import database
from app import db


class ProdusOld():
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


class Categorie(db.Model):
    __tablename__ = 'categorie'
    idCategorie = db.Column(db.Integer, autoincrement=True, primary_key=True)
    NumeCategorie = db.Column(db.text)


class Magazin(db.Model):
    __tablename__ = 'magazin'
    idMagazin = db.Column(db.Integer, autoincrement=True, primary_key=True)
    Nume = db.Column(db.text)
    LinkMagazin = db.Column(db.text)
    Descriere = db.Column(db.text)

    def __repr__(self):
        return "Magazin: {magazin} ".format(magazin=self.Nume)


class Pret(db.Model):
    __tablename__ = 'pret'
    idPret = db.Column(db.Integer, autoincrement=True, primary_key=True)
    idProdus = db.Column(db.Integer, db.ForeignKey('produs.idProdus'))
    NumeProdus = db.relationship('Produs', backref=db.backref('pret',
                                                              lazy='dynamic'))
    Pret = db.Column(db.DECIMAL(10, 4))
    Data = db.Column(db.Date)


class Produs(db.Model):
    __tablename__ = 'produs'
    idProdus = db.Column(db.Integer, autoincrement=True, primary_key=True)
    idCategorie = db.Column(db.Integer, db.ForeignKey('categorie.idCategorie'),
                            default=0)
    NumeCategorie = db.relationship('Categorie',
                                    backref=db.backref('produs',
                                                       lazy='dynamic'))
    idMagazin = db.Column(db.Integer, db.ForeignKey('categorie.idMagazin'))
    Nume = db.relationship('Magazin', backref=db.backref('produs',
                                                         lazy='dynamic'))
    NumeProdus = db.Column(db.text)
    LinkProdus = db.Column(db.text)
    PozaProdus = db.Column(db.text)
    hash = db.Column(db.VARCHAR(40))

    def __repr__(self):
        return "Produs: {nume_produs} \nLink Produs: {link_produs}".\
            format(nume_produs=self.NumeProdus, link_produs=self.LinkProdus)