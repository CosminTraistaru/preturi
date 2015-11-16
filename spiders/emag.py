__author__ = 'bobo'

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from items import Product
from utils.filters import *
import re


class EmagSpider(CrawlSpider):

    name = 'emag'

    allowed_domains = ['emag.ro']

    start_urls = ["http://www.emag.ro/"]

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//*[contains(@class, "emg-menu-list")]',
                    '//*[contains(@class, "emg-pagination-no")]',
                    '//*[contains(@class, "category-sidebar")]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=True,
        ),
    )

    def process_page(self, response):
        products = response.css('.product-holder-grid')
        products.extract()

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('.//form/h2/a/text()').extract()[0]
            link = selection.xpath('.//form/h2/a/@href').extract()[0]
            img = selection.xpath('.//form/div/a/span/img/@data-src').extract()[0]
            price_int = selection.xpath('.//span[@class="money-int"]/text()').extract()[0]
            price_decimal = selection.xpath('.//sup[@class="money-decimal"]/text()').extract()[0]

            link = "http://www.emag.ro" + link
            img = re.sub('^//', 'http://', img)
            price = int(str(price_int).translate(None, '.,'))+(0.01 * int(price_decimal))

            product['title'] = title.strip()
            product['price'] = price
            product['link'] = link.strip()
            product['image'] = img.strip()

            yield product