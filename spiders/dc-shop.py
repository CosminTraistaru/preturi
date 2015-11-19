# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class DCShopSpider(CrawlSpider):
    name = 'dc-shop'
    allowed_domains = ['dc-shop.ro']
    start_urls = ['http://www.dc-shop.ro/']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//div[@class="MenuLeft"]',
                    '//div[@class="pageresults"]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=False,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//div[@class="productlisting"]/div[@class="productListing-tot"]')

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('./div[@class="productListing-nume"]/h2/a/text()').extract()[0]
            link = selection.xpath('./div[@class="productListing-poza"]/a/@href').extract()[0]
            img = selection.xpath('./div[@class="productListing-poza"]/a/img/@src').extract()[0]
            price = selection.xpath('./div[@class="productListing-pret"]/div[@class="pret_n"]/b/text()').extract()[0]

            # Remove caracthers and keep numbers
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title
            product['price'] = float(price)
            product['link'] = link
            product['image'] = img

            yield product