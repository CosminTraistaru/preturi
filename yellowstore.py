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
shop_id = db_connection.get_shop_id('yellowstore')

DELAY = 10
categories = []
subcategories = []
url = "http://shop.yellowstore.ro/"
LIST_OF_LINKS = []
DATE = "%d-%m-%y"
LONG_DATE = "%d-%m-%y %H-%M"


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
        print "\n!!! caca !!!- {0}".format(link)
        error_file.write("\n{0} - Timeout exception - {1}\n".
                         format(time.strftime(LONG_DATE), link))
        pass
    except NameError as e:
        error_file.write("\n{0} - Page was not loaded exception - {1} - {2}\n".
                         format(time.strftime(LONG_DATE),
                                e, link))
        pass
    except Exception as e:
        error_file.write("\n{0} - Some error - {1} - {2}\n".format(
            time.strftime(LONG_DATE), e, link))
    error_file.close()
    return None


def _get_name(soup):
    soup_response = soup.find(attrs={"id": "image"})['alt']
    text = unicodedata.normalize('NFKD', soup_response).encode('ascii', 'ignore')
    return str(text.replace(',', '').replace('#', ''))


def _get_price(soup):
    if not soup.find_all(class_='price'):
        return "N/A"
    text = soup.find_all(class_='price')[-1].text
    some_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    match = re.search(r'^\d+', str(some_text).replace('.', '').replace('\n', ''))
    price = match.group()
    return int(price)


def _get_stoc(soup):
    text = soup.find(class_='availability').text
    working_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    return working_text.replace('\n', '')


def _get_image(soup):
    if soup.find(attrs={"id": "image"}):
        image = soup.find(attrs={"id": "image"})['src']
    else:
        image = "N/A"
    return str(image)


def get_subcats():
    soup = get_soup(url)
    if not soup:
        return
    parents1 = soup.find_all(attrs={"id": "parent-1"})
    for parent in parents1:
        parent2 = parent.find_all(attrs={"id": "parent-2"})
        if not parent2:
            link = parent.find('a')['href']
            subcategories.append(link)
        else:
            for links in parent2:
                for link in links.find_all('a'):
                    subcategories.append(link['href'])


def get_links_for_products():
    for subcat in subcategories:
        soup = get_soup(subcat)
        if not soup:
            continue
        items = soup.find_all(class_='item')
        for item in items:
            link = item.find('a')['href']
            LIST_OF_LINKS.append(link)


def get_product_info():
    global db_connection
    global scrape_date
    global shop_id
    csv_file = open('csv/yellowstore/yellowstore-{0}.csv'.format(
        time.strftime(DATE)), 'ab')
    yellowstore = csv.writer(csv_file)
    for link in LIST_OF_LINKS:
        soup = get_soup(link)
        if not soup:
            continue
        product = soup.find(class_='product-essential')
        name = _get_name(product)
        price = _get_price(product)
        availability = _get_stoc(product)
        image = _get_image(product)
        entry = (name, price, availability, str(link), image)
        produs = (name, price, link, image)
        db_connection.insert_product(produs, shop_id, scrape_date)

        print entry
        yellowstore.writerow(entry)
    csv_file.close()


get_subcats()
get_links_for_products()
get_product_info()

db_connection.commit()
