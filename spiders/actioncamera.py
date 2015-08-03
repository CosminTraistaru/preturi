# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *


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
            process_links='filter',
            callback='process_page',
            follow=True,
        ),
    )

    def filter(self, links):
        accepted_links = filter_links(links, 'black')

        for link in accepted_links:
            print link

        return accepted_links

    def process_page(self, response):
        products = response.xpath('//ol[@id="products-list"]/li')
        products.extract()

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('./div/div/h2/a/text()').extract()[0]
            link = selection.xpath('./div/div/h2/a/@href').extract()[0]
            img = selection.xpath('./a[contains(@class, "product-image")]/img/@src').extract()[0]
            price = selection.xpath('./div/div/div/span[contains(@class, "regular-price")]/span/text()').extract()

            if len(price) == 0:
                price = selection.xpath('./div/div/div/p[contains(@class, "special-price")]/span/text()').extract()[0]
            else:
                price = price[0]

            product['title'] = title.strip()
            product['price'] = price.strip()
            product['link'] = link.strip()
            product['image'] = img.strip()

            yield product