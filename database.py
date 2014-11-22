__author__ = 'bobo'

import mysql.connector
from mysql.connector import errorcode
import mysql_conf
import hashlib


def connect_db(config=None):
    connection = None
    if not config:
        config = mysql_conf.mysqlconfig
    try:
        connection = mysql.connector.connect(**config)
        print("Connected to database")
        connection.autocommit = True
    except mysql.connector.Error as error:
        if error.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied to database")
        elif error.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Unable to select database")
        else:
            print(error)
    return connection


def disconnect_db(connection):
    connection.close()
    print("Disconnected from db")


def insert_product(product, shop_id, scrape_date, connection):
    added_product = 0
    added_price = 0
    insert_product_price = False

    product_name = product[0]
    product_price = product[1]
    product_link = product[2]
    product_img = product[3]

    product_hash = hashlib.sha1(product_name + product_link).hexdigest()
    product_id = get_product_id(product_hash, connection)

    if product_id == 0:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO `produs` (`idProdus`, `idCategorie`, `idMagazin`, `NumeProdus`, "
                       "`LinkProdus`, `PozaProdus`, `hash`) VALUES (NULL, '0', %s, %s, %s, %s, %s)",
                       (shop_id, product_name, product_link, product_img, product_hash))
        product_id = cursor.lastrowid

        added_product = 1

        insert_product_price = True
        cursor.close()
    else:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM `pret` "
                       "WHERE `pret`.`idProdus`= %s AND `pret`.`Data` = %s", (product_id, scrape_date))

        if len(cursor.fetchall()) == 0:
            insert_product_price = True

        cursor.close()

    if insert_product_price:
        cursor = connection.cursor()

        cursor.execute("INSERT INTO `pret` (`idPret`, `idProdus`, `Pret`, `Data`) "
                       "VALUES (NULL, %s, %s, %s)", (product_id, product_price, scrape_date))

        added_price = 1

        cursor.close()

    result = (added_product, added_price)

    return result


def get_product_id(product_hash, connection):
    cursor = connection.cursor()

    cursor.execute("SELECT produs.idProdus FROM produs WHERE produs.hash = %s", (product_hash, ))

    result = cursor.fetchall()

    if not result:
        product_id = 0
    else:
        product_id = result[0][0]

    cursor.close()

    return product_id


def get_shop_id(shop_name, connection):
    cursor = connection.cursor()

    cursor.execute("SELECT magazin.idMagazin FROM magazin  WHERE magazin.Nume LIKE %s", (shop_name, ))
    result = cursor.fetchall()
    cursor.close()

    if result is None:
        cursor = connection.cursor()

        cursor.execute("INSERT INTO `magazin` (`idMagazin`, `Nume`, `LinkMagazin`, `Descriere`) VALUES "
                       "(NULL, %s, '', '');", (shop_name, ))

        shop_id = cursor.lastrowid
    else:
        shop_id = result[0]

    return shop_id
