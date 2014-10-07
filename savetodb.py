#!/usr/bin/env python
__author__ = 'bobo'

import csv
import mysql.connector
from mysql.connector import errorcode

from mysql_conf import *

connection = None


def connect_db(config):
    try:
        global connection
        connection = mysql.connector.connect(**config)
        print("Connected to database")
    except mysql.connector.Error as error:
        if error.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied to database")
        elif error.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Unable to select database")
        else:
            print(error)


def disconnect_db():
    connection.close()


def process_csv(file):
    with open(file, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            print("Produs: %s ,pret: %d", row[0], row[1])

process_csv('csv/emag/emag-07-10-14.csv')