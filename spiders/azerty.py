# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class AzertySpider(CrawlSpider):
    name = 'azerty'
    allowed_domains = ['azerty.ro']
    start_urls = ['http://www.azerty.ro/']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//div[@id="navigation"]',
                    '//div[@class="paginationtop"]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=False,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//div[@class="pcontainerlist"]/div[@class="box_produs"]')

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('./div[@class="specs"]/div/a/text()').extract()[0]
            link = selection.xpath('./a/@href').extract()[0]
            img = selection.xpath('./a/img/@src').extract()[0]
            price = selection.xpath('./ul/li[1]/span[2]/text()').extract()[0]

            # Remove caracthers and keep numbers
            link = "http://www.azerty.ro" + link.strip()
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title
            product['price'] = float(price)
            product['link'] = link
            product['image'] = img

            yield product