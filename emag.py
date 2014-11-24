#!/usr/bin/env python

import time
import csv
import re

import requests
import unicodedata

from bs4 import BeautifulSoup
from selenium import webdriver

import base

import database

DELAY = 10
categories = []
subcategories = []
WANTED = ["laptopuri",
          "telefoane",
          "tablete",
          "monitoare",
          "desktop",
          "router",
          "televizoare",
          "home-cinema",
          "audio",
          "mediaplayer",
          "foto",
          "obiective",
          "blitzuri",
          "dsrl",
          "camere",
          "console-",
          "genti",
          "mouse",
          "tastaturi",
          "espressor",
          "casti",
          "boxe",
          "ipod",
          "ebook",
          "memorii",
          "placi_baza",
          "placi_video",
          "ssd",
          "nas",
          "spalat",
          "fiare",
          "frigorifice",
          "anvelope-auto",
          "receiver",
          "electrocasnice",
          "incorporabile",
          "cuptoare",
          "conditionat",
          "espressor",
          ]

db_connection = database.connect_db()
scrape_date = time.strftime("%Y-%m-%d")
shop_id = database.get_shop_id('emag', db_connection)

def do_stuff():
    """
    This method retrieves all the links to all subcategories from emag.ro
    It's the only method that uses selenium with the PhantomJS browser
    """
    driver = webdriver.Firefox()
    driver.get("http://www.emag.ro")
    category_list = \
        driver.find_elements_by_css_selector(".menuSecondaryList .column a")
    for category in category_list:
        categories.append(category.get_attribute("href"))
    f = open("subcategories-emag.txt", 'w')
    for category in categories:
        driver.get(category)
        subcategory_list = driver.find_elements_by_css_selector(
            "#continut .category-sidebar a")
        time.sleep(5)
        for subcategory in subcategory_list:
            if "http://openx4.emag.ro" in subcategory.get_attribute("href"):
                continue
            if 'filter' in subcategory.get_attribute("href"):
                continue
            f.write("{}\n".format(subcategory.get_attribute("href")))
            subcategories.append(subcategory.get_attribute("href"))
    f.close()
    driver.quit()


def get_name(title):
    return ' '.join(
        [re.sub('[^A-Za-z0-9.]+', '', word) for word in title.split()]
    )


def get_availability(av):
    available = unicodedata.normalize('NFKD', av).encode('ascii', 'ignore')
    return available.replace('\n', '').replace('  ', '')


def get_number_of_pages(div):
    pages = unicodedata.normalize('NFKD', div).encode('ascii', 'ignore')
    return int(pages.replace('\n', '').replace('  ', '')[-2:])


def get_page(url):
    pass


def write_to_log(message):
    pass


def get_prices(url):
    global db_connection
    global shop_id
    global scrape_date

    current_page = 0
    page = requests.get(url)
    soup = BeautifulSoup(page.text)
    number_of_pages = get_number_of_pages(soup.find(class_='left-part').text)
    with open('csv/emag/emag-{0}.csv'.format(
            time.strftime("%d-%m-%y")), 'ab') as csv_file:
        emag_db = csv.writer(csv_file)
        while current_page <= number_of_pages:
            soup = BeautifulSoup(page.text)
            products = soup.find_all(attrs={"name": "product[]"})
            for product in products:
                name = get_name(product.find_next("a")['title'])
                price = str(product.find_next(class_='money-int').
                            text.replace('.', ''))
                availability = get_availability(
                    product.find_next(class_='stare-disp-listing').text)
                link = "http://www.emag.ro{0}".format(
                    product.find_next("a")['href'])
                image = product.find_next('img')['src']
                entry = (name, price, availability, link, image)
                produs = (name, price, link, image)

                database.insert_product(produs, shop_id, scrape_date, db_connection)
                emag_db.writerow(entry)
            current_page += 1
            time.sleep(DELAY)
            page_url = "{0}p{1}/c".format(url[:-1], current_page)
            page = base.get_page_content(page_url)
            while not page:
                if current_page > number_of_pages:
                    break
                current_page += 1
                time.sleep(DELAY)
                page_url = "{0}p{1}/c".format(url[:-1], current_page)
                page = base.get_page_content(page_url)
            print current_page + 1


def run():
    visited_categories = []
    # Using a log file to store all the subcategories from which we know the
    # prices from, we read the visited categories from the log a put them in a
    # list.
    logs = open('logs/emag-{0}.log'.format(time.strftime("%d-%m-%y")), 'a')
    logs.close()
    # Not the cleanest way of making sure that the file exists
    logs = open('logs/emag-{0}.log'.format(time.strftime("%d-%m-%y")), 'r+')
    for cat in logs:
        visited_categories.append(cat)
    list_of_categories = open("subcategories-emag.txt", 'r')
    for category in list_of_categories:
        go = False
        for interest in WANTED:
            if interest in category:
                go = True
                break
        print category
        if not go:
            print "Category is not interesting"
            continue
        if category in visited_categories:
            # if the subcategory is already in the log the script skips it.
            print "This category already read"
            continue
        else:
            response = requests.get(category)
            if not response.ok:
                print "Link not available"
                continue
            get_prices(category[:-1])
            logs.write("{0}".format(category))
            time.sleep(DELAY)
    logs.close()


if __name__ == '__main__':
    # do_stuff()
    run()
    database.disconnect_db(db_connection)
