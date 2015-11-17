# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class MediadotSpider(CrawlSpider):
    name = 'mediadot'
    allowed_domains = ['mediadot.ro']
    start_urls = ['http://www.mediadot.ro/']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//div[@id="navigation"]',
                    '//div[@class="paginatie"]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=False,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//div[@id="produse"]/div[@class="product_box"]')

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('./div[@class="description"]/h2/a/text()').extract()[0]
            link = selection.xpath('./div/a/@href').extract()[0]
            img = selection.xpath('./div/a/img/@src').extract()[0]
            price = selection.xpath('./div[@class="price"]/span/text()').extract()[0]

            # Remove caracthers and keep numbers
            link = "http://www.mediadot.ro" + link.strip()
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title
            product['price'] = float(price)
            product['link'] = link
            product['image'] = img

            yield product