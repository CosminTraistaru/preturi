# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class PCShopSpider(CrawlSpider):
    name = 'pc-shop'
    allowed_domains = ['pc-shop.ro']
    start_urls = ['http://www.pc-shop.ro/']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//div[@id="menu"]',
                    '//div[@class="pagination"]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=False,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//div[@class="oferta_produs"]')

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('./div/div[@class="titlu_produs"]/a/text()').extract()[0]
            link = selection.xpath('./div/div[@class="titlu_produs"]/a/@href').extract()[0]
            img = selection.xpath('./div/div[@class="imagine_produs"]/a/img[not(contains(@class, "promo"))]/@src').extract()[0]
            price = selection.xpath('./div/div/div[@class="pret"]/span[@class="valoare" and not(@style)]/text()').extract()[0]

            # Remove caracthers and keep numbers
            link = "http://www.pc-shop.ro" + link.strip()
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title.strip()
            product['price'] = float(price)
            product['link'] = link
            product['image'] = img.strip()

            yield product