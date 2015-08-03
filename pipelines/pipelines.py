# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class PricexpertPipeline(object):
    def __init__(self):
        print "Pipeline created"

    def __del__(self):
        print "Pipeline deleted"

    def process_item(self, item, spider):
        return item
