#!/usr/bin/env python

import re
import time
import csv

import requests
import unicodedata

from bs4 import BeautifulSoup


DELAY = 0
categories = []
temp_subcategories = []
subcategories = []
url = "http://www.flanco.ro/"


def get_soup(link):
    req = requests.get(link)
    return BeautifulSoup(req.text)


def get_subcategories():
    soup = get_soup(url)
    level0 = soup.find_all(class_='level0')
    for cat in level0:
        if 'jucarii' in cat.find('a')['href']:
            continue
        categories.append(cat.find('a')['href'])
    for cat in categories:
        soup = get_soup(cat)
        # print cat
        menu = soup.find(attrs={"id": "narrow-by-list2"}).find_all('li')
        for subcat in menu:
            temp_subcategories.append(subcat.find('a')['href'])
        for s in temp_subcategories:
            soup = get_soup(s)
            if soup.find(attrs={"id": "narrow-by-list2"}):
                menu = soup.find(attrs={"id": "narrow-by-list2"}).find_all('li')
                for subcat in menu:
                    subcategories.append(subcat.find('a')['href'])
            else:
                subcategories.append(s)


def get_number_of_pages(soup):
    text = soup.find(class_='amount').text.replace('  ', '')
    match = re.search(r'\d+$', text)
    if match:
        products = int(match.group())
        no_of_pages = int(products/50) + 1
    else:
        no_of_pages = 1
    return no_of_pages


def get_price(text):
    match = re.search(r'^\d+', str(text))
    return match.group()


def get_availability(code):
    av = unicodedata.normalize('NFKD', code).encode('ascii', 'ignore')
    return av


def get_info_from_product(product):
    name = product.find('a')['title']
    link = product.find('a')['href']
    image = product.find('img')['href']
    price = get_price(product.find(class_='price').text)
    availability = get_availability(product.find(class_='in-stock').text)
    print name, price, availability, link, image
    return name, price, availability, link, image


def get_products():
    csv_file = open('csv/flanco/flanco-{0}.csv'.format(
        time.strftime("%d-%m-%y")), 'ab')
    flanco_db = csv.writer(csv_file)
    get_subcategories()
    for s in subcategories:
        soup = get_soup("{0}?limit=50".format(s))
        number_of_pages = get_number_of_pages(soup)
        for page_no in xrange(1, number_of_pages+1):
            addr = "{0}?limit=50?p={1}".format(s, page_no)
            soup = get_soup(addr)
            product_list = soup.find(class_='products-list')
            products = product_list.find_all(class_='item')
            for product in products:
                entry = get_info_from_product(product)
                flanco_db.writerow(entry)
                print entry
    csv_file.close()


get_products()
