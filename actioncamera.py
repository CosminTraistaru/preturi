#!/usr/bin/env python
__author__ = 'ctraistaru'

import time
import csv
import unicodedata
import re

import requests

from bs4 import BeautifulSoup

import database

DELAY = 10
categories = [
    "http://www.actioncamera.ro/camere-video-online.html",
    "http://www.actioncamera.ro/prinderi-camere-video-actiune.html",
    "http://www.actioncamera.ro/accesorii.html"
]


def go_to_next_page(link, page_number):
    error_file = open("error.log", 'a')
    url = "{0}?p={1}".format(link, page_number)
    try:
        time.sleep(DELAY)
        page = requests.get(url)
        if not page.ok:
            time.sleep(DELAY)
            page = requests.get(url)
            if not page.ok:
                raise NameError("Page was not loaded")
        return page.text
    except requests.Timeout:
        print "!!! caca !!!- {0}".format(url)
        error_file.write("{0} - Timeout exception - {1}\n".
                         format(time.strftime("%d-%m-%y %H-%M"), url))
        pass
    except NameError as e:
        error_file.write("{0} - Page was not loaded exception - {1} - {2}\n".
                         format(time.strftime("%d-%m-%y %H-%M"),
                                e, url))
        pass
    except Exception as e:
        error_file.write("{0} - Some error - {1} - {2}\n".format(
            time.strftime("%d-%m-%y %H-%M"), e, url))
    error_file.close()
    return None


def get_price(code):
    if code.find(class_='special-price'):
        correct_price = code.find(class_='special-price').find(class_='price').text
    else:
        correct_price = code.find(class_='price').text
    long_price = unicodedata.normalize('NFKD', correct_price).encode('ascii', 'ignore')
    match = re.search(r'^\d+', str(long_price).replace('.', '').replace('  ', '').replace('\n', ''))
    return match.group()


def get_product_info(product):
    price = get_price(product.find(class_='price-box'))
    name = product.find(class_='product-name').find('a')['title']
    link = product.find(class_='product-name').find('a')['href']
    image = "N/A"  # str(product.find('img')['pagespeed_lazy_src'])
    availability = "N/A"
    return name, price, availability, link, image


def db():
    csv_file = open('csv/actioncamera/actioncamera-{0}.csv'.format(
        time.strftime("%d-%m-%y")), 'ab')
    db_connection = database.connect_db()
    shop_id = database.get_shop_id('actioncamera', db_connection)
    scrape_date = time.strftime("%Y-%m-%d")
    actioncamera_db = csv.writer(csv_file)
    for cat in categories:
        req = requests.get(cat)
        time.sleep(DELAY)
        soup = BeautifulSoup(req.text)
        links_to_no_of_pages = soup.find(class_='pages')
        number_of_pages = int(links_to_no_of_pages.find_all('a')[-2].text)
        print cat
        print number_of_pages
        for page_no in xrange(1, number_of_pages+1):
            soup = BeautifulSoup(go_to_next_page(cat, page_no))
            products_list = soup.find(class_="products-list")
            for product in products_list.find_all(class_='item'):
                entry = get_product_info(product)
                produs = (entry[0], entry[1], entry[3], entry[4])
                database.insert_product(produs, shop_id, scrape_date, db_connection)
                actioncamera_db.writerow(entry)
    csv_file.close()
    database.disconnect_db(db_connection)


db()
