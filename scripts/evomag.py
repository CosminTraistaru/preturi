__author__ = 'ctraistaru'


import time
import re

import requests

from bs4 import BeautifulSoup


categories = []
subcategories = []
ce_vrem = []


def do_stuff():
    page = requests.get("http://www.evomag.ro")
    soup = BeautifulSoup(page.text)
    category_list = soup.find_all(class_="left_category_subcategory_container")
    for category in category_list:
        categories.append(category.next['href'])
    print categories

    for category in categories:
        time.sleep(2)
        page = requests.get("http://www.evomag.ro{}".format(category))
        print page.url
        try:
            soup = BeautifulSoup(page.text)
            subcategory_div = soup.find_all(class_="categorie_sumar")[0]
            subcategory_list = subcategory_div.find_all('a')
            for sub in subcategory_list:
                if 'htm' in sub:
                    continue
                if 'javascript'in sub:
                    continue
                if sub in categories:
                    continue
                if sub['href'] in subcategories:
                    continue
                subcategories.append(sub['href'])
        except IndexError as e:
            print e.message
            pass
    f = open("subcategories-evomag.txt", 'w')
    for s in subcategories:
        f.write("http://www.evomag.ro{}\n".format(s))
        print s
    f.close()


def get_prices(url="http://www.emag.ro/laptopuri/c"):
    page = requests.get(url)
    soup = BeautifulSoup(page.text)
    last_page = soup.find_all(class_='last')[-1]
    pages = last_page.find('a')['href']
    match = re.search(r'\d+$', pages)
    number_of_pages = int(match.group())

    produse = soup.find_all(attrs={"name": "product[]"})
    produse = soup.find_all(class_='prod_list_det')
    for produs in produse:
        print produs.find_next("a")['title']
        print produs.find_next(class_='money-int').text




do_stuff()