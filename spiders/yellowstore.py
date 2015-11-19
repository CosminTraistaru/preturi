# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class YellowstoreSpider(CrawlSpider):
    name = 'yellowstore'
    allowed_domains = ['yellowstore.ro']
    start_urls = ['http://www.yellowstore.ro/']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//div[@id="new_categories"]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=False,
        ),
    )

    def process_page(self, response):
        if response.xpath('//ol[@id="products-list"]/li[contains(@class, "list-default")]'):
            products = response.xpath('//ol[@id="products-list"]/li[contains(@class, "list-default")]')
            layout = "grid"
        else:
            products = response.xpath('//ol[@id="products-list"]/li[contains(@class, "list-accesorii")]')
            layout = "list"

        for index, selection in enumerate(products):
            product = Product()

            if layout == "list":
                # We are not interested in bundles
                if selection.xpath('./div/div[contains(@id, "package-slider")]'):
                    continue

                title = selection.xpath('./div[contains(@class, "product-shop")]/h2/a/text()').extract()[0]
                link = selection.xpath('./div[contains(@class, "product-block")]/a/@href').extract()[0]
                img = selection.xpath('./div[contains(@class, "product-block")]/a/img/@src').extract()[0]
                price = selection.xpath('./div[contains(@class, "block-right")]/div/div/span[@class="price"]').extract()[0]

            elif layout == "grid":
                title = selection.xpath('./div/div/h2/a/text()').extract()[0]
                link = selection.xpath('./a/@href').extract()[0]
                img = selection.xpath('./a/img/@src').extract()[0]
                price = selection.xpath('./div/div/div/span[@class="price"]').extract()[0]

            # Remove caracthers and keep numbers
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title
            product['price'] = float(price)
            product['link'] = link
            product['image'] = img

            yield product