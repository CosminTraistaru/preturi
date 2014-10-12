#!/usr/bin/env python
__author__ = 'bobo'

import csv
import mysql.connector
from mysql.connector import errorcode
import mysql_conf

connection = None
cursor = None


def connect_db(config):
    try:
        global connection
        global cursor
        connection = mysql.connector.connect(**config)
        print("Connected to database")
        connection.autocommit = True
        cursor = connection.cursor()
        print cursor
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
    global cursor

    with open(file_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            nume_produs = row[0]
            link_produs = row[3]
            img_produs = row[4]
            id_produs = get_product_id(nume_produs)

            if id_produs == 0:
                query = ("INSERT INTO `produs` (`idProdus`, `idCategorie`, `idMagazin`, `NumeProdus`, `LinkProdus`, `PozaProdus`) "
                    "VALUES ('0', '0', '1', '"+nume_produs+"', '"+link_produs+"', '"+img_produs+"')")
                cursor.execute(query)


            else:
                pass


def get_product_id(product_name):
    global cursor

    query = "SELECT produs.idProdus FROM produs as produs WHERE produs.NumeProdus LIKE '%"+product_name+"%' "

    cursor.execute(query)

    result = cursor.fetchone()

    if result is None:
        product_id = 0
    else:
        product_id = result[0]

    return product_id


indice = get_product_id("Gig")
print indice
#process_csv('csv/emag/emag-07-10-14.csv')
disconnect_db()