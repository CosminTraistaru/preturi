import time
import csv
import unicodedata
import re
import requests

from bs4 import BeautifulSoup
from selenium import webdriver


categories = []
subcategories = []


def do_stuff():
    """
    This method retrieves all the links to all subcategories from emag.ro
    It's the only method that uses selenium with the PhantomJS browser
    """
    driver = webdriver.PhantomJS()
    driver.get("http://www.emag.ro")
    category_list = \
        driver.find_elements_by_css_selector(".menuSecondaryList .column a")
    for category in category_list:
        categories.append(category.get_attribute("href"))
    f = open("subcategories-emag.txt", 'a')
    for category in categories:
        driver.get(category)
        subcategory_list = driver.find_elements_by_css_selector(
            "#continut .category-sidebar a")
        time.sleep(5)
        for subcategory in subcategory_list:
            if "http://openx4.emag.ro" in subcategory.get_attribute("href"):
                continue
            f.write("{}\n".format(subcategory.get_attribute("href")))
            print subcategory.get_attribute("href")
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


def get_page_content(url):
    error_file = open("error.log", 'a')
    try:
        page = requests.get(url, timeout=40)
        if not page.ok:
            time.sleep(10)
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


def get_prices(url):
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
                emag_db.writerow(entry)
            current_page += 1
            time.sleep(15)
            page_url = "{0}p{1}/c".format(url[:-1], current_page)
            page = get_page_content(page_url)
            while not page:
                if current_page > number_of_pages:
                    break
                current_page += 1
                time.sleep(15)
                page_url = "{0}p{1}/c".format(url[:-1], current_page)
                page = get_page_content(page_url)
            print current_page + 1


def run():
    visited_categories = []
    # Using a log file to store all the subcategories from which we know the
    # prices from, we read the visited categories from the log a put them in a
    # list.
    logs = open('logs/emag-{0}.log'.format(time.strftime("%d-%m-%y")), 'r+')
    for cat in logs:
        visited_categories.append(cat)
    list_of_categories = open("subcategories-emag.txt", 'r')
    for category in list_of_categories:
        if category in visited_categories:
            # if the subcategory is already in the log the script skips it.
            print "This category already read"
            continue
        else:
            print category
            get_prices(category[:-1])
            logs.write("{0}\n".format(category))
            time.sleep(15)
    logs.close()

if __name__ == '__main__':
    run()
