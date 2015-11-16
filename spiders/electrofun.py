# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class ElectrofunSpider(CrawlSpider):
    name = 'electrofun'
    allowed_domains = ['electrofun.ro']
    start_urls = ['http://www.electrofun.ro/']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//div[contains(@class, "main_menu")]',
                    '//*[@id="x-pages_id"]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=True,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//div[@id="x-products-container"]/div[contains(@class, "x-product-line")]')
        products.extract()

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('./h3/a/text()').extract()[0]
            link = selection.xpath('./h3/a/@href').extract()[0]
            img = selection.xpath('./table/tr/td[contains(@class, "x-product-image")]/div/a/img/@src').extract()[0]
            price = selection.xpath('./table/tr/td[contains(@class, "x-product-controls")]/p/span/text()').extract()[0]

            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title.strip()
            product['price'] = float(price)
            product['link'] = link.strip()
            product['image'] = img.strip()

            yield product
