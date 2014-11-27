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



