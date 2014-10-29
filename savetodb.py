#!/usr/bin/env python
__author__ = 'bobo'

import csv
import datetime
import hashlib
import re
import mysql.connector
import os
from mysql.connector import errorcode
import mysql_conf

connection = None
nr_added_products = 0
nr_added_prices = 0
current_nr_products = 0
current_nr_prices = 0
start_timestamp = None
csv_start_timestamp = None


def connect_db(config):
    try:
        global connection
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


def disconnect_db():
    connection.close()
    print("Disconnected from db")


def process_csv(file_name):
    global nr_added_products
    global nr_added_prices

    match = re.match("^.+/([a-zA-Z0-9]+)-([0-9]{2})-([0-9]{2})-([0-9]{2}).+", file_name)

    shop_id = get_shop_id(match.group(1))
    date = datetime.datetime.strptime(match.group(4)+match.group(3)+match.group(2), "%y%m%d")
    scrape_date = date.strftime("%Y-%m-%d")

    with open(file_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:

            insert_product_price = False
            product_name = row[0]
            product_price = row[1]
            product_link = row[3]
            product_img = row[4]
            product_hash = hashlib.sha1(product_name+product_link).hexdigest()
            product_id = get_product_id(product_hash)

            if product_id == 0:
                cursor = connection.cursor()
                query = ("INSERT INTO `produs` "
                         "(`idProdus`, `idCategorie`, `idMagazin`, `NumeProdus`, `LinkProdus`, `PozaProdus`, `hash`) "
                         "VALUES (NULL, '0', '" + str(shop_id) + "', '" + product_name + "', '" + product_link + "', '" +
                         product_img + "', '" + product_hash + "')")
                cursor.execute(query)
                product_id = cursor.lastrowid
                nr_added_products += 1
                insert_product_price = True
                cursor.close()
            else:
                if False:
                    cursor = connection.cursor()
                    query = ("SELECT * FROM `produs` WHERE `idProdus`=" + str(product_id))
                    cursor.execute(query)
                    result = cursor.fetchall()
                    print "In baza de date\t: "+ result[0][3] + "\t" + result[0][4] + "\t" + result[0][5]
                    print "In csv\t\t\t: " + product_name + "\t" + product_link + "\t" + product_img
                    cursor.close()

                cursor = connection.cursor()
                query = ("SELECT * FROM `pret` "
                         "INNER JOIN `produs` ON `pret`.`idProdus` = `produs`.`idProdus` "
                         "WHERE `produs`.`idProdus`=" + str(product_id) + " "
                         " AND `pret`.`Data` = '" + scrape_date + "' ")
                cursor.execute(query)

                if not cursor.with_rows:
                    insert_product_price = True
                else:
                    cursor.fetchall()

                cursor.close()

            if insert_product_price:
                cursor = connection.cursor()
                query = ("INSERT INTO `pret` "
                         "(`idPret`, `idProdus`, `Pret`, `Data`) "
                         "VALUES (NULL, '"+str(product_id)+"', '"+str(product_price)+"', '"+scrape_date+"')")
                cursor.execute(query)
                nr_added_prices += 1
                cursor.close()


def get_product_id(product_hash):
    cursor = connection.cursor()

    query = "SELECT produs.idProdus FROM produs WHERE produs.hash = '"+product_hash+"' "

    cursor.execute(query)

    result = cursor.fetchall()

    if not result:
        product_id = 0
    else:
        product_id = result[0][0]

    cursor.close()

    return product_id


def get_shop_id(shop_name):

    cursor = connection.cursor()
    query = "SELECT magazin.idMagazin FROM magazin  WHERE magazin.Nume LIKE '%"+shop_name+"%' "

    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()

    if result is None:
        cursor = connection.cursor()
        query = ("INSERT INTO `magazin` "
                 "(`idMagazin`, `Nume`, `LinkMagazin`, `Descriere`) VALUES "
                 "(NULL, '"+shop_name+"', '', '');")
        cursor.execute(query)

        shop_id = cursor.lastrowid
    else:
        shop_id = result[0]

    return shop_id


def traverse_folder(path):
    global nr_added_products
    global nr_added_prices
    global current_nr_products
    global current_nr_prices
    global start_timestamp
    global csv_start_timestamp

    for entry in os.listdir(path):
        if os.path.isdir(path+"/"+entry):
            traverse_folder(path+"/"+entry)
        else:
            if nr_added_products != 0:
                current_nr_products = nr_added_products - current_nr_products
                print "Added " + str(current_nr_products) + " products"
            if nr_added_prices != 0:
                current_nr_prices = nr_added_prices - current_nr_prices
                print "Added prices for " + str(current_nr_prices) + " products"
            if start_timestamp is not None:
                print "Processing time: " + str(datetime.datetime.now() - csv_start_timestamp)
            else:
                start_timestamp = datetime.datetime.now()
            print "Processing :" + path+"/"+entry
            csv_start_timestamp = datetime.datetime.now()
            process_csv(path+"/"+entry)


connect_db(mysql_conf.mysqlconfig)

traverse_folder("csv/pcfun")

disconnect_db()

print "Total products :" + str(nr_added_products)
print "Total prices: " + str(nr_added_prices)
print "Total process time: " + str(datetime.datetime.now() - start_timestamp)