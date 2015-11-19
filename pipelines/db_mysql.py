__author__ = 'bobo'

import hashlib
import random

import mysql.connector
from mysql.connector import errorcode

from config import db_mysql_conf


class PricexpertMySQLSave:
    connection = None
    cursor = None
    temporary_pret_table = ""
    temporary_produs_table = ""

    shop_id = None

    def __init__(self, autocommit=False, config=None):
        self.connection = None
        if not config:
            config = db_mysql_conf.mysqlconfig
        try:
            self.connection = mysql.connector.connect(**config)
            print "Connected to DB"
            self.cursor = self.connection.cursor()

            self.connection.autocommit = autocommit

            if not autocommit:
                table_suffix = hashlib.sha1(str(random.random() * 65000)).hexdigest()
                self.temporary_pret_table = self.create_temporary_table_pret(table_suffix)
                self.temporary_produs_table = self.create_temporary_table_produs(table_suffix)

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

    def create_temporary_table_pret(self, table_suffix):
        query = "CREATE TABLE IF NOT EXISTS `pret_%s` (" \
                "`idProdus` varchar(40) NOT NULL," \
                "`Pret` decimal(10,4) NOT NULL," \
                "`Data` date NOT NULL," \
                "PRIMARY KEY (`idProdus`,`Data`)" \
                ") ENGINE=InnoDB DEFAULT CHARSET=latin1;" % table_suffix
        self.cursor.execute(query)
        return "pret_" + table_suffix

    def create_temporary_table_produs(self, table_suffix):
        query = "CREATE TABLE IF NOT EXISTS `produs_%s` (" \
                "`idProdus` varchar(40) NOT NULL," \
                "`idCategorie` int(11) NOT NULL DEFAULT '0'," \
                "`idMagazin` int(11) NOT NULL," \
                "`NumeProdus` text NOT NULL," \
                "`LinkProdus` text NOT NULL," \
                "`PozaProdus` text NOT NULL," \
                "PRIMARY KEY (`idProdus`)" \
                ") ENGINE=InnoDB DEFAULT CHARSET=latin1;" % table_suffix
        self.cursor.execute(query)
        return "produs_" + table_suffix

    def open_spider(self, spider):
        self.shop_id = self.get_shop_id(spider.name)

    def close_spider(self, spider):
        self.commit()

    def process_item(self, item, spider):

        product_name = item['title']
        product_price = item['price']
        product_link = item['link']
        product_img = item['image']

        scrape_date = "CURRENT_TIMESTAMP"

        product_hash = hashlib.sha1((product_name + product_link).encode('utf-8')).hexdigest()
        product_id = self.get_product_id(product_hash)

        if product_id == 0:
            query = "INSERT INTO %s (`idProdus`, `idCategorie`, `idMagazin`, `NumeProdus`, `LinkProdus`, `PozaProdus`) " \
                    "VALUES (%%s, '0', %%s, %%s, %%s, %%s)" % self.temporary_produs_table

            self.cursor.execute(query, (product_hash, self.shop_id, product_name, product_link, product_img))

        try:
            query = "INSERT INTO %s (`idProdus`, `Pret`, `Data`) VALUES (%%s, %%s, %%s)" % self.temporary_pret_table

            self.cursor.execute(query, (product_hash, product_price, scrape_date))

        except mysql.connector.IntegrityError:
            pass

        return item

    def get_product_id(self, product_hash):
        query = "SELECT EXISTS(SELECT 1 FROM `%s` WHERE `idProdus` = %%s)" % self.temporary_produs_table
        self.cursor.execute(query, (product_hash, ))

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
        try:
            query = "INSERT IGNORE INTO `produs` SELECT * FROM `%s`" % self.temporary_produs_table
            self.cursor.execute(query)

            query = "INSERT IGNORE INTO `pret` SELECT * FROM %s" % self.temporary_pret_table
            self.cursor.execute(query)

        except:
            pass

        query = "DROP TABLE `%s`" % self.temporary_produs_table
        self.cursor.execute(query)

        query = "DROP TABLE %s" % self.temporary_pret_table
        self.cursor.execute(query)

        self.connection.commit()