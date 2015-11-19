# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class MarketonlineSpider(CrawlSpider):
    name = 'marketonline'
    allowed_domains = ['marketonline.ro']
    start_urls = ['http://www.marketonline.ro/']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//div[@id="menu-container"]',
                    '//div[@class="pagination"]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=False,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//div[@id="centercolumn"]/div[@class="productbox"]')

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('./p[@class="title"]/span/a/text()').extract()[0]
            link = selection.xpath('./p[@class="title"]/span/a/@href').extract()[0]
            img = selection.xpath('./div[@class="image"]/a/img/@src').extract()[0]
            price = selection.xpath('./div[@class="description"]/div/span/text()').extract()[1]

            # Remove caracthers and keep numbers
            link = "http://www.marketonline.ro" + link.strip()
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title
            product['price'] = float(price)
            product['link'] = link
            product['image'] = img

            yield product