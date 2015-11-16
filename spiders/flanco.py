# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product
from utils.filters import *
import re


class FlancoSpider(CrawlSpider):
    name = 'flanco'
    allowed_domains = ['flanco.ro']
    # start_urls = ['http://www.flanco.ro/']
    start_urls = ['http://www.flanco.ro/computere-periferice/gaming/jocuri-pc.html']
    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    # '//ul[@id="gan_nav_top"]',
                    # '//a[contains(@class, "next")]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=False,
        ),
    )

    def process_page(self, response):
        products = response.xpath('//ol[@id="products-list"]/li')

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('.//h2[@class="product-name"]/a/text()').extract()[0]
            link = selection.xpath('.//h2[@class="product-name"]/a/@href').extract()[0]
            img = selection.xpath('.//a[@class="product-image"]/img/@data-src').extract()[0]

            pricebox = selection.xpath('./div/div/div/div')

            if pricebox.xpath('./p[@class="special-price"]/span[@class="price"]/span'):
                price = pricebox.xpath('./p[@class="special-price"]/span[@class="price"]/span/text()').extract()[0]
            elif pricebox.xpath('./span/span'):
                price = pricebox.xpath('./span/span/text()').extract()[0]

            # Remove caracthers and keep numbers
            price = re.sub('[^0-9,]+', '', price.strip())
            price = re.sub(',', '.', price)

            product['title'] = title
            product['price'] = float(price)
            product['link'] = link
            product['image'] = img

            yield product