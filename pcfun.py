#!/usr/bin/env python

__author__ = 'ctraistaru'

import time
import re
import csv

import unicodedata
import requests

from bs4 import BeautifulSoup

CATEGORIES = []
SUBCATEGORIES = []
# CE_VREM = []
DELAY = 10


def do_stuff():
    """
    This method gets all the subcategories from the site, and saves them
    to a file.
    """
    page = requests.get("http://www.pcfun.ro")
    soup = BeautifulSoup(page.text)
    for main_categ in soup.find_all(class_='main_categ'):
        SUBCATEGORIES.append(str(main_categ['href']))
    for subcateg in soup.find_all(class_='subcateg'):
        SUBCATEGORIES.append(str(subcateg['href']))
    f = open("subcategories-pcfun.txt", 'w')
    for s in SUBCATEGORIES:
        f.write("{}\n".format(s))
    f.close()


def get_name(title):
    new_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
    return ' '.join(
        [re.sub('[^A-Za-z0-9.()]+', '', word) for word in new_title.split()]
    )


def get_price(text):
    match = re.search(r'^\d+', str(text).replace('.', ''))
    return match.group()


def get_page_content(url):
    error_file = open("error.log", 'a')
    try:
        page = requests.get(url, timeout=40)
        if not page.ok:
            time.sleep(DELAY)
            page = requests.get(url, timeout=40)
            if not page.ok:
                raise NameError("Page was not loaded")
        return page
    except requests.Timeout:
        print "!!! caca !!!- {0}".format(url)
        error_file.write("{0} - Timeout exception - {1}\n".
                         format(time.strftime("%d-%m-%y %H-%M"), url))
        pass
    except NameError as e:
        error_file.write("{0} - Page was not loaded exception - {1} - {2}\n".
                         format(time.strftime("%d-%m-%y %H-%M"),
                                e.message, url))
        pass
    except Exception as e:
        error_file.write("{0} - Some error - {1} - {2}\n".format(
            time.strftime("%d-%m-%y %H-%M"), e.message, url))
    error_file.close()
    return None


def get_number_of_pages(text):
    match = re.search(r'\d+/$', str(text))
    if match:
        return int(match.group()[:-1])
    else:
        return 1


def get_prices(url="http://www.pcfun.ro/ultrabook/"):
    page = requests.get(url)
    current_page = 1
    soup = BeautifulSoup(page.text)
    number_of_pages = get_number_of_pages(soup.find(class_='x-pages-more').
        find_previous('a')['href'])
    with open('csv/pcfun/pcfun-{0}.csv'.format(
            time.strftime("%d-%m-%y")), 'ab') as csv_file:
        pcfun_db = csv.writer(csv_file)
        while current_page <= number_of_pages:
            soup = BeautifulSoup(page.text)
            products = soup.find_all(class_='x-product-line')
            for product in products:
                name = get_name(product.find_next('a').text)
                link = product.find_next('a')['href']
                imagine = product.find_next('img')['src']
                availability = str(product.find_next('strong').text)
                price = get_price(str(product.find_next(class_='price_tag').text))
                entry = (name, price, availability, link, imagine)
                pcfun_db.writerow(entry)
            current_page += 1
            page_url = "{0}pagina{1}/".format(url, current_page)
            page = get_page_content(page_url)
            time.sleep(DELAY)
            print current_page
            while not page:
                if current_page > number_of_pages:
                    break
                current_page += 1
                time.sleep(DELAY)
                page_url = "{0}pagina{1}/".format(url, current_page)
                page = get_page_content(page_url)


def run():
    logs = open('logs/pcfun-{0}.log'.format(time.strftime("%d-%m-%y")), 'a')
    logs.close()

    for sub in SUBCATEGORIES:
        go = True
        # for interest in CE_VREM:
        #     if interest in sub:
        #         go = True
        #         break
        with open('logs/pcfun-{0}.log'.format(time.strftime("%d-%m-%y")), 'r') as logs:
            for log in logs:
                if sub in log:
                    go = False
        try:
            if not requests.get(sub).ok:
                time.sleep(DELAY)
                go = False
        except requests.ConnectionError as e:
            error_file = open("error.log", 'a')
            error_file.write("{0} {1} {2}\n".format(time.strftime("%d-%m-%y %H-%M"),
                                                    e.message, sub))
            error_file.close()
            go = False
            pass
        print sub
        if not go:
            print "Category is not interesting"
            continue
        try:
            get_prices(sub)
        except TypeError as e:
            error_file = open("error.log", 'a')
            error_file.write("{0} {1} {2}\n".format(time.strftime("%d-%m-%y %H-%M"),
                                                    e.message, sub))
            error_file.close()
            pass
        except Exception as e:
            error_file = open("error.log", 'a')
            error_file.write("{0} {1} {2}\n".format(time.strftime("%d-%m-%y %H-%M"),
                                                    e.message, sub))
            error_file.close()
            pass

        logs = open('logs/pcfun-{0}.log'.format(time.strftime("%d-%m-%y")), 'a')
        logs.write("{}\n".format(sub))
        logs.close()



do_stuff()
run()