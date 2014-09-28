__author__ = 'ctraistaru'


import time
import re
import csv

import requests

from bs4 import BeautifulSoup


categories = []
subcategories = []
ce_vrem = ["PORTABILE",
           "SISTEME-PC",
           "COMPONENTE-PC",
           "SOLUTII-MOBILE",
           "TELEVIZOARE",
           "MONITOARE",
           "Imprimante",
           "Multifunctionale",
           "FOTO",
           "VIDEO",
           "MULTIMEDIA",
           "GAMING",
           "RETELISTICA",
           "AUTO"]
DELAY = 10
SITE_URL = "http://www.evomag.ro"


def do_stuff():
    page = requests.get("http://www.evomag.ro")
    soup = BeautifulSoup(page.text)
    category_list = soup.find_all(class_="left_category_subcategory_container")
    for category in category_list:
        categories.append(category.next['href'])
    for category in categories:
        time.sleep(DELAY)
        page = requests.get("http://www.evomag.ro{}".format(category))
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
        print "!!! caca !!!- {}".format(url)
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


def get_name(title):
    return ' '.join(
        [re.sub('[^A-Za-z0-9.()]+', '', word) for word in title.split()]
    )


def get_price(text):
    match = re.search(r'^\d+', str(text).replace('.', ''))
    return match.group()


def get_stoc(text):
    return str(text).replace('\r', '').replace('\n', '').replace('\t', '').\
        replace('  ', '')


def get_prices(url):
    page = requests.get(url)
    current_page = 1
    soup = BeautifulSoup(page.text)
    last_page = soup.find_all(class_='last')[-1]
    pages = last_page.find('a')['href']
    match = re.search(r'\d+$', pages)
    if match is None:
        number_of_pages = 1
    else:
        number_of_pages = int(match.group())
    print number_of_pages
    with open('csv/evomag/evomag-{0}.csv'.format(
            time.strftime("%d-%m-%y")), 'ab') as csv_file:
        evomag_db = csv.writer(csv_file)
        while current_page <= number_of_pages:
            soup = BeautifulSoup(page.text)
            produse = soup.find_all(class_='prod_list_det')
            for produs in produse:
                name = get_name(produs.find_next("a")['title'])  # titlu
                price = get_price(produs.find(class_='discount_span').
                                  previous_sibling)
                link = "{}{}".format(SITE_URL, produs.find('a')['href'])
                imagine = "{}{}".format(SITE_URL, produs.find('img')['src'])
                availability = get_stoc(produs.find
                                        (class_='stoc_produs').
                                        find_next('span').text)
                entry = (name, price, availability, link, imagine)
                evomag_db.writerow(entry)
            current_page += 1
            page_url = "{}{}{}".format(url, "Filtru/Pagina:", current_page)
            page = get_page_content(page_url)
            while not page:
                if current_page > number_of_pages:
                    break
                current_page += 1
                time.sleep(DELAY)
                page_url = "{}{}{}".format(url, "Filtru/Pagina:", current_page)
                page = get_page_content(page_url)


def run():
    subcats = []
    # do_stuff()
    logs = open('logs/evomag-{0}.log'.format(time.strftime("%d-%m-%y")), 'a')
    logs.close()
    with open("subcategories-evomag.txt", 'r') as f:
        for cat in f:
            subcats.append(str(cat).replace('\n', ''))
    for sub in subcats:
        go = False
        for interest in ce_vrem:
            if interest in sub:
                go = True
                break
        with open('logs/evomag-{0}.log'.format(time.strftime("%d-%m-%y")), 'r') as logs:
            for log in logs:
                if sub in log:
                    go = False
        try:
            if not requests.head(sub).ok:
                go = False
        except requests.ConnectionError as e:
            error_file = open("error.log", 'a')
            error_file.write("{} {} {}\n".format(time.strftime("%d-%m-%y %H-%M"),
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
        except Exception as e:
            error_file = open("error.log", 'a')
            error_file.write("{} {} {}\n".format(time.strftime("%d-%m-%y %H-%M"),
                                                 e.message, sub))
            error_file.close()
            pass
        except TypeError as e:
            error_file = open("error.log", 'a')
            error_file.write("{} {} {}\n".format(time.strftime("%d-%m-%y %H-%M"),
                                                 e.message, sub))
            error_file.close()
            pass

        logs = open('logs/evomag-{0}.log'.format(time.strftime("%d-%m-%y")), 'a')
        logs.write("{}\n".format(sub))
        logs.close()


do_stuff()
run()
