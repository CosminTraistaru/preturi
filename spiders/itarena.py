# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class ItarenaSpider(CrawlSpider):
    name = 'itarena'
    allowed_domains = ['itarena.ro']
    start_urls = ['http://www.itarena.ro/']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//div[@class="menu-header-body"]',
                    '//div[contains(@class, "pagination")]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=False,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//div[@class="items"]/div[@class="row-fluid"]')

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('./div/div/div/div/div/div/h4[@class="product-title"]/a/text()').extract()[0]
            link = selection.xpath('./div/div/div/div/div/div/h4[@class="product-title"]/a/@href').extract()[0]
            img = selection.xpath('./div/div/div/div/div/div[contains(@class, "image")]/a/img/@src').extract()[0]
            price = selection.xpath('./div/div/div/div/div[contains(@class, "product-list-price")]/text()').extract()[0]

            # Remove caracthers and keep numbers
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title
            product['price'] = float(price)
            product['link'] = link
            product['image'] = img

            yield product