#!/usr/bin/env python

import re
import time
import csv

import requests
import unicodedata

from bs4 import BeautifulSoup

import database

db_connection = database.Database()
scrape_date = time.strftime("%Y-%m-%d")
shop_id = db_connection.get_shop_id('flanco')

DELAY = 8
categories = []
temp_subcategories = []
subcategories = []
url = "http://www.flanco.ro/"
DATE = time.strftime("%d-%m-%y")
LONG_DATE = time.strftime("%d-%m-%y %H-%M")


def get_soup(link):
    error_file = open("error.log", 'a')
    try:
        time.sleep(DELAY)
        req = requests.get(link)
        if not req.ok:
            time.sleep(DELAY)
            req = requests.get(link)
            if not req.ok:
                raise NameError("Page was not loaded")
        return BeautifulSoup(req.text)
    except requests.Timeout:
        print "!!! caca !!!- {0}".format(link)
        error_file.write("{0} - Timeout exception - {1}\n".format(LONG_DATE, link))
        pass
    except NameError as e:
        error_file.write("{0} - Page was not loaded exception - {1} - {2}\n".
                         format(LONG_DATE, e, link))
        pass
    except Exception as e:
        error_file.write("{0} - Some error - {1} - {2}\n".format(LONG_DATE, e, link))
    error_file.close()
    return None


def get_subcategories():
    soup = get_soup(url)
    level0 = soup.find_all(class_='level0')
    for cat in level0:
        if 'jucarii' in cat.find('a')['href']:
            continue
        categories.append(cat.find('a')['href'])
    for cat in categories:
        soup = get_soup(cat)
        menu = soup.find(attrs={"id": "narrow-by-list2"}).find_all('li')
        for subcat in menu:
            temp_subcategories.append(subcat.find('a')['href'])
        for s in temp_subcategories:
            soup = get_soup(s)
            if not soup:
                continue
            if soup.find(attrs={"id": "narrow-by-list2"}):
                menu = soup.find(attrs={"id": "narrow-by-list2"}).find_all('li')
                for subcat in menu:
                    subcategories.append(subcat.find('a')['href'])
            else:
                subcategories.append(s)


def _get_number_of_pages(soup):
    text = soup.find(class_='amount').text.replace('  ', '').replace('\n', '')
    match = re.search(r'\d+$', text)
    if match:
        products = int(match.group())
        no_of_pages = int(products/10) + 1
    else:
        no_of_pages = 1
    return no_of_pages


def _get_price(text):
    match = re.search(r'^\d+', str(text).replace('.', '').replace('\n', ''))
    if match:
        return int(match.group())
    else:
        return 'N/A'


def _get_name(text):
    working_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    return working_text.replace(',', '')


def _get_availability(code):
    av = unicodedata.normalize('NFKD', code).encode('ascii', 'ignore')
    return av


def found_an_error(err):
    error_file = open("error.log", 'a')
    error_file.write(err)
    error_file.close()


def _get_info_from_product(product):
    name = _get_name(product.find(class_='product-name').text)
    link = str(product.find('a')['href'])
    image = str(product.find(class_='lazy')['data-src'])
    if product.find(class_='price'):
        price = _get_price(product.find(class_='price').text)
    else:
        found_an_error("The product {0}, has no price!!! Set to 0".format(name))
        price = 0
    if product.find(class_='availability'):
        availability = _get_availability(product.find(class_='availability').text)
    else:
        availability = "N/A"
    return name, price, availability, link, image


def get_products():
    global db_connection
    global scrape_date
    global shop_id

    csv_file = open('csv/flanco/flanco-{0}.csv'.format(DATE), 'ab')
    flanco_db = csv.writer(csv_file)
    get_subcategories()
    for s in subcategories:
        soup = get_soup(s)
        if not soup:
            continue
        if not soup.find(class_='amount'):  # if not landing subcategory page
            continue
        number_of_pages = _get_number_of_pages(soup)
        for page_no in xrange(1, number_of_pages+1):
            addr = "{0}?p={1}".format(s, page_no)
            soup = get_soup(addr)
            if not soup:
                continue
            product_list = soup.find(class_='products-list')
            if not product_list:
                continue
            products = product_list.find_all(class_='item')
            entries = map(_get_info_from_product, products)
            for entry in entries:
                produs = (entry[0], entry[1], entry[3], entry[4])
                db_connection.insert_product(produs, shop_id, scrape_date)

            flanco_db.writerows(entries)
    csv_file.close()


get_products()
db_connection.commit()
