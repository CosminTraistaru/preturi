#!/usr/bin/env python

import time
import re
import csv

import unicodedata
import requests

from bs4 import BeautifulSoup

import base

import database

CATEGORIES = []
SUBCATEGORIES = []
# CE_VREM = []
DELAY = 10
DATE = time.strftime("%d-%m-%y")

db_connection = database.connect_db()
scrape_date = time.strftime("%Y-%m-%d")
shop_id = database.get_shop_id('electrofun', db_connection)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}


def do_stuff():
    """
    This method gets all the subcategories from the site, and saves them
    to a file.
    """
    page = requests.get("http://www.electrofun.ro", headers=headers)
    soup = BeautifulSoup(page.text)
    for main_categ in soup.find_all(class_='main_categ'):
        SUBCATEGORIES.append(str(main_categ['href']))
    for subcateg in soup.find_all(class_='subcateg'):
        SUBCATEGORIES.append(str(subcateg['href']))
    f = open("subcategories-pcfun.txt", 'w')
    for s in SUBCATEGORIES:
        f.write("{0}\n".format(s))
    f.close()


def get_name(title):
    new_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
    return ' '.join(
        [re.sub('[^A-Za-z0-9.()]+', '', word) for word in new_title.split()]
    )


def get_price(text):
    match = re.search(r'\d+', str(text).replace('.', ''))
    return match.group()


def get_number_of_pages(text):
    match = re.search(r'\d+/$', str(text))
    if match:
        return int(match.group()[:-1])
    else:
        return 1


def get_prices(url="http://www.electrofun.ro/aparate-pentru-bucatarie/masini-de-tocat/"):
    global db_connection
    global scrape_date
    global shop_id

    page = requests.get(url, headers=headers)
    current_page = 1
    soup = BeautifulSoup(page.text)
    if not soup.find(class_='x-pages'):
        return
    number_of_pages = get_number_of_pages(soup.find(class_='x-pages').
        find_all('a')[-1]['href'])
    with open('csv/electrofun/electrofun-{0}.csv'.format(DATE), 'ab') as csv_file:
        pcfun_db = csv.writer(csv_file)
        while current_page <= number_of_pages:
            soup = BeautifulSoup(page.text)
            products = soup.find_all(class_='x-product-line')
            for product in products:
                name = get_name(product.find_next('a').text)
                link = product.find_next('a')['href']
                imagine = product.find_next('img')['src']
                availability = str(product.find_next('strong').text)
                price = get_price(str(product.find(class_='price_tag').text))
                entry = (name, price, availability, link, imagine)
                produs = (name, price, link, imagine)
                database.insert_product(produs, shop_id, scrape_date, db_connection)
                pcfun_db.writerow(entry)
            current_page += 1
            page_url = "{0}pagina{1}/".format(url, current_page)
            page = base.get_page_content(page_url)
            time.sleep(DELAY)
            print current_page
            while not page:
                if current_page > number_of_pages:
                    break
                current_page += 1
                time.sleep(DELAY)
                page_url = "{0}pagina{1}/".format(url, current_page)
                page = base.get_page_content(page_url)


def run():
    logs = open('logs/electrofun-{0}.log'.format(DATE), 'a')
    logs.close()

    for sub in SUBCATEGORIES:
        go = True
        with open('logs/electrofun-{0}.log'.format(DATE), 'r') as logs:
            for log in logs:
                if sub in log:
                    go = False
        try:
            if not requests.get(sub, headers=headers).ok:
                time.sleep(DELAY)
                go = False
        except requests.ConnectionError as e:
            error_file = open("error.log", 'a')
            error_file.write("{0} {1} {2}\n".format(DATE, e, sub))
            error_file.close()
            go = False
            pass
        print sub
        if not go:
            print "Category is not interesting"
            continue
        try:
            get_prices(sub)
        except (TypeError, Exception) as e:
            error_file = open("error.log", 'a')
            error_file.write("{0} {1} {2}\n".format(DATE, e, sub))
            error_file.close()
            pass

        logs = open('logs/electrofun-{0}.log'.format(DATE), 'a')
        logs.write("{0}\n".format(sub))
        logs.close()


do_stuff()
run()

database.disconnect_db(db_connection)