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

            self.connection.autocommit = True

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
        added_price = 0
        insert_product_price = False

        product_name = product[0]
        product_price = product[1]
        product_link = product[2]
        product_img = product[3]

        product_hash = hashlib.sha1(product_name + product_link).hexdigest()
        product_id = self.get_product_id(product_hash)

        if product_id == 0:

            self.cursor.execute("INSERT INTO `produs` (`idProdus`, `idCategorie`, `idMagazin`, `NumeProdus`, "
                                "`LinkProdus`, `PozaProdus`, `hash`) VALUES (NULL, '0', %s, %s, %s, %s, %s)",
                                (shop_id, product_name, product_link, product_img, product_hash))
            product_id = self.cursor.lastrowid

            added_product = 1

            insert_product_price = True
        else:
            self.cursor.execute("SELECT * FROM `pret` "
                                "WHERE `pret`.`idProdus`= %s AND `pret`.`Data` = %s", (product_id, scrape_date))

            if len(self.cursor.fetchall()) == 0:
                insert_product_price = True

        if insert_product_price:
            self.cursor.execute("INSERT INTO `pret` (`idPret`, `idProdus`, `Pret`, `Data`) "
                                "VALUES (NULL, %s, %s, %s)", (product_id, product_price, scrape_date))

            added_price = 1

        result = (added_product, added_price)

        return result

    def get_product_id(self, product_hash):

        self.cursor.execute("SELECT produs.idProdus FROM produs WHERE produs.hash = %s", (product_hash, ))

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
