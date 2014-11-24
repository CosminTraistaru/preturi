#!/usr/bin/env python

import re
import time
import csv

import requests
import unicodedata

from bs4 import BeautifulSoup

import database

db_connection = database.connect_db()
scrape_date = time.strftime("%Y-%m-%d")
shop_id = database.get_shop_id('f64', db_connection)

DELAY = 10
categories = []
subcategories = []
url = "http://www.f64.ro/"


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
                         format(time.strftime("%d-%m-%y %H-%M"), link))
        pass
    except NameError as e:
        error_file.write("\n{0} - Page was not loaded exception - {1} - {2}\n".
                         format(time.strftime("%d-%m-%y %H-%M"),
                                e, link))
        pass
    except Exception as e:
        error_file.write("\n{0} - Some error - {1} - {2}\n".format(
            time.strftime("%d-%m-%y %H-%M"), e, link))
    error_file.close()
    return None


def get_subcats(soup):
    subcats = []
    links = soup.find_all('a')
    for link in links:
        subcats.append(link['href'])
    return subcats


def get_subcategories():
    soup = get_soup(url)
    level0 = soup.find_all(class_='t')
    for cat in level0:
        subcat = cat.find(class_='sub')
        if subcat:
            subcats = get_subcats(subcat)
            map(subcategories.append, subcats)
        else:
            subcats = cat.find('a')['href']
            subcategories.append(subcats)


def _get_link(soup):
    try:
        product = soup.find(class_='product_title')
        link = str(product.find('a')['href'])
    except UnicodeEncodeError:
        return "N/A"
    return link


def _get_name(soup):
    heading = soup.find(class_='product_title')
    text = heading.find('h2').text
    working_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    return working_text.replace(',', '').replace('#', '')


def _get_price(soup):
    if not soup.find(class_='price_list_int'):
        return "N/A"
    text = soup.find(class_='price_list_int').text
    match = re.search(r'^\d+', str(text).replace('.', '').replace('\n', ''))
    price = match.group()[:-2]
    return int(price)


def _get_stoc(soup):
    text = soup.find(class_='stock_price_new').text
    working_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    return working_text.replace('\n', '')


def _get_image(soup):
    if soup.find('img'):
        image = soup.find('img')['src']
    else:
        image = "N/A"
    return str(image)


def get_product_info(soup):
    product_info = soup.find(class_='prod_list')
    if product_info:
        image = _get_image(product_info)
        name = _get_name(product_info)
        link = _get_link(product_info)
        price = _get_price(product_info)
        availability = _get_stoc(product_info)
    else:
        return None
    print name, price, availability, link, image
    return name, price, availability, link, image


def _get_nr_of_pages(soup):
    d = soup.find(class_='d')
    if not d:
        return 1
    p = d.find_next('a').text
    return int(p)


def get_prices():
    global db_connection
    global scrape_date
    global shop_id

    csv_file = open('csv/f64/f64-{0}.csv'.format(time.strftime("%d-%m-%y")), 'ab')
    f64_db = csv.writer(csv_file)
    get_subcategories()
    for subcategory in subcategories:
        soup = get_soup(subcategory)
        number_of_pages = _get_nr_of_pages(soup)
        for page in xrange(1, number_of_pages+1):
            if not page == 1:
                soup = get_soup("{0}-p{1}.html".format(subcategory[:-5], page))
            if not soup:
                continue
            list_of_products = soup.find_all(class_='product_list_container')
            if not list_of_products:
                print subcategory
            entries = map(get_product_info, list_of_products)
            for entry in entries:
                produs = (entry[0], entry[1], entry[3], entry[4])
                database.insert_product(produs, shop_id, scrape_date, db_connection)

            f64_db.writerows(entries)
            print page
    csv_file.close()


get_prices()
database.disconnect_db(db_connection)

# !!! Not all the pages from f64 are visited, wierd page numbering system on
# some pages