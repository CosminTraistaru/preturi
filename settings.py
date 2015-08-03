# -*- coding: utf-8 -*-

# Scrapy settings for pricexpert project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
from utils.useragents import *
import socket

hostname = socket.gethostname()

BOT_NAME = 'pricexpert'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_DEBUG = True
DOWNLOAD_DELAY = 1

ITEM_PIPELINES = {
    'pipelines.db_mysql.PricexpertMySQLSave': 300,
}

USER_AGENT = get_random_user_agent()

if hostname == "bobo-VirtualBox":
    DOWNLOADER_MIDDLEWARES = {
        'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 100,
    }

