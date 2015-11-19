# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class F64Spider(CrawlSpider):
    name = 'f64'
    allowed_domains = ['f64.ro']
    start_urls = ['http://www.f64.ro/']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//ul[@id="menu_nav"]',
                    '//div[@class="pages_container_div"]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=True,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//div[@class="product_list_container"]')

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('./table/tr/td[@class="product_title"]/a/h2/text()').extract()[0]
            link = selection.xpath('./table/tr/td[@class="product_title"]/a/@href').extract()[0]

            if selection.xpath('./table/tr/td[@class="image_container"]/div/table/tr/td/a/img/@src'):
                img = selection.xpath('./table/tr/td[@class="image_container"]/div/table/tr/td/a/img/@src').extract()[0]
            elif selection.xpath('./table/tr/td[@class="image_container"]/div/table/tr/td/a/@rel'):
                img = selection.xpath('./table/tr/td[@class="image_container"]/div/table/tr/td/a/@rel').extract()[0]

            price_int = selection.xpath('./table/tr/td[@class="product_details_right"]/table/tr/td/table/tr/td/div/span[@class="price_list_int"]/text()').extract()[0]
            price_decimal = selection.xpath('./table/tr/td[@class="product_details_right"]/table/tr/td/table/tr/td/div/span[@class="price_list_int"]/sup/text()').extract()[0]

            price = price_int + "," + price_decimal
            # Clean up vars
            # Remove caracthers and keep numbers
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title.strip()
            product['price'] = float(price)
            product['link'] = link.strip()
            product['image'] = img.strip()
            print product
            # yield product