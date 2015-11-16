# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class EvomagSpider(CrawlSpider):
    name = 'evomag'
    allowed_domains = ['evomag.ro']
    start_urls = ['http://www.evomag.ro/RETELISTICA-Routere']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//ul[contains(@class, "ulMeniu")]',
                    '//a[contains(@class, "next")]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=False,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//div[contains(@class, "produse_liste_filter")]/div[contains(@class, "prod_list_det tabel-view")]')
        products.extract()

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('.//div[contains(@class, "list_product_title")]/h2/a/text()').extract()[0]
            link = selection.xpath('.//div[contains(@class, "list_product_title")]/h2/a/@href').extract()[0]
            img = selection.xpath('.//div/a/img[last()]/@src').extract()[0]
            price = selection.xpath('.//div[contains(@class, "price_block_list")]/text()').extract()[1]

            # Remove caracthers and keep numbers
            link = "http://www.evomag.ro" + link.strip()
            img = "http://www.evomag.ro" + img.strip()
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title
            product['price'] = float(price)
            product['link'] = link
            product['image'] = img

            yield product