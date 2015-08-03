# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from items import Product


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
                    '//li[contains(@class, "next")]',
                )
            ),
            process_links='filter_links',
            callback='process_page',
            follow=False,
        ),
    )

    def filter_links(self, links):

        #for link in links:
        #    print link.url

        return links

    def process_page(self, response):
        products = response.xpath('//*[contains(@class, "prod_list_det")]')
        products.extract()

        for index, selection in enumerate(products):
            product = Product()

            title = selection.xpath('.//div[contains(@class, "list_product_title")]/h2/text()').extract()
            link = selection.xpath('.//div/div/div/h2/a/@href').extract()
            img = selection.xpath('.//div/a/img[last()]/@src').extract()
            #price_int = selection.xpath('.//span[@class="money-int"]/text()').extract()[0]
            #price_decimal = selection.xpath('.//sup[@class="money-decimal"]/text()').extract()[0]
            #price = int(str(price_int).translate(None, '.,'))+(0.01 * int(price_decimal))

            #product['title'] = title.strip()
            #product['price'] = price
            #product['link'] = link.strip()
            #product['image'] = img.strip()
            print title
            #yield product