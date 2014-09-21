__author__ = 'ctraistaru'

from bs4 import BeautifulSoup
import time
from selenium import webdriver

categories = []
subcategories = []


def do_stuff():
    driver = webdriver.PhantomJS()
    driver.get("http://www.evomag.ro")
    soup = BeautifulSoup(driver.page_source)
    category_list = soup.find_all(class_="left_category_subcategory_container")
    for category in category_list:
        categories.append(category.next['href'])

    for category in categories:
        time.sleep(5)
        driver.get("http://www.evomag.ro{}".format(category))
        print driver.current_url
        soup = BeautifulSoup(driver.page_source)
        subcategory_div = soup.find_all(class_="categorie_sumar")[0]
        subcategory_list = subcategory_div.find_all('a')
        for sub in subcategory_list:
            subcategories.append(sub['href'])

    f = open("subcategories-evomag.txt", 'w')
    for s in subcategories:
        f.write("http://www.evomag.ro{}\n".format(s))
        print s
    f.close()
    driver.quit()


# def get_prices(url="http://www.emag.ro/laptopuri/c"):
#     driver = webdriver.PhantomJS()
#     driver.get(url)
#     soup = BeautifulSoup(driver.page_source)
#     produse = soup.find_all(attrs={"name": "product[]"})
#     for produs in produse:
#         print produs.find_next("a")['title']
#         print produs.find_next(class_='money-int').text
#     driver.quit()

    # forward = driver.find_elements_by_class_name("pagination-arrow")
    # for f in forward:
    #     if f.text == ">":
    #         f.click()


do_stuff()