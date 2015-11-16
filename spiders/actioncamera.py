# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class ActioncameraSpider(CrawlSpider):

    name = 'actioncamera'

    allowed_domains = ['actioncamera.ro']

    start_urls = [
        'http://www.actioncamera.ro',
        ]

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//ul[contains(@class, "level0")]/li/a',
                    '//a[contains(@class, "next")]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=True,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//ol[@id="products-list"]/li')
        products.extract()

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('./div/div/h2/a/text()').extract()[0]
            link = selection.xpath('./div/div/h2/a/@href').extract()[0]
            img = selection.xpath('./a[contains(@class, "product-image")]/img/@src').extract()[0]
            pricebox = selection.xpath('./div/div/div[contains(@class, "price-box")]')

            if pricebox.xpath('./span[contains(@class, "regular-price")]'):
                price = pricebox.xpath('./span[contains(@class, "regular-price")]/span[contains(@class, "price")]/text()').extract()[0]
            elif pricebox.xpath('./p[contains(@class, "special-price")]'):
                price = pricebox.xpath('./p[contains(@class, "special-price")]/span[contains(@class, "price")]/text()').extract()[1]

            # Clean up vars
            # Remove caracthers and keep numbers
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title.strip()
            product['price'] = float(price)
            product['link'] = link.strip()
            product['image'] = img.strip()

            yield product