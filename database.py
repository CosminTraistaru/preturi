__author__ = 'bobo'

import mysql.connector
from mysql.connector import errorcode
import mysql_conf
import hashlib


class Database:
    connection = None
    cursor = None

    def __init__(self, config=None):
        self.connection = None
        if not config:
            config = mysql_conf.mysqlconfig
        try:
            self.connection = mysql.connector.connect(**config)

            self.connection.autocommit = False

            self.cursor = self.connection.cursor()

        except mysql.connector.Error as error:
            if error.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Access denied to database")
            elif error.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                print("Unable to select database")
            else:
                print(error)

    def __del__(self):
        self.connection.close()
        print("Disconnected from db")

    def insert_product(self, product, shop_id, scrape_date):
        added_product = 0

        product_name = product[0]
        product_price = product[1]
        product_link = product[2]
        product_img = product[3]

        product_hash = hashlib.sha1(product_name + product_link).hexdigest()
        product_id = self.get_product_id(product_hash)

        if product_id == 0:

            self.cursor.execute("INSERT INTO `produs` (`idProdus`, `idCategorie`, `idMagazin`, `NumeProdus`, "
                                "`LinkProdus`, `PozaProdus`) VALUES (%s, '0', %s, %s, %s, %s)",
                                (product_hash, shop_id, product_name, product_link, product_img))

            added_product = 1

        try:
            self.cursor.execute("INSERT INTO `pret` (`idProdus`, `Pret`, `Data`) "
                                "VALUES (%s, %s, %s)", (product_hash, product_price, scrape_date))
            added_price = 1
        except mysql.connector.IntegrityError:
            added_price = 0

        result = (added_product, added_price)

        return result

    def get_product_id(self, product_hash):

        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM produs WHERE produs.idProdus = %s)", (product_hash, ))

        result = self.cursor.fetchall()
        if len(result) == 0:
            product_id = 0
        else:
            product_id = result[0][0]

        return product_id

    def get_shop_id(self, shop_name):

        self.cursor.execute("SELECT magazin.idMagazin FROM magazin  WHERE magazin.Nume LIKE %s", (shop_name, ))
        result = self.cursor.fetchall()

        if len(result) == 0:

            self.cursor.execute("INSERT INTO `magazin` (`idMagazin`, `Nume`, `LinkMagazin`, `Descriere`) VALUES "
                                "(NULL, %s, '', '');", (shop_name, ))

            shop_id = self.cursor.lastrowid
        else:

            shop_id = result[0][0]

        return shop_id

    def commit(self):
        self.connection.commit();