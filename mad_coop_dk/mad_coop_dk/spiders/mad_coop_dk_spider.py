# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class mad_coop_dk_spiderSpider(scrapy.Spider):

    name = "mad_coop_dk_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(mad_coop_dk_spiderSpider, self).__init__(*args, **kwargs)

        if not categories:
            raise CloseSpider('Received no categories!')
        else:
            self.categories = categories
        self.start_urls = loads(self.categories).keys()

        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'
        }

###########################################################

    def start_requests(self):
        for url in self.start_urls:
            #link = "https://mad.coop.dk" + url
            cat1, cat2 = url.split("#!")
            link = "https://mad.coop.dk/api/catalog/search?category1={}&category2={}&getTagManagerScript=true&listViewType=0&page=1&term=-&pageSize=".format(cat1.strip("/"),cat2.strip("/"))
            yield Request(
                    link+"1", 
                    self.parse_categories, 
                    meta={"categories":url, "deep":0, "url":link}, 
                    headers=self.headers)

###########################################################
    def parse_categories(self, response):
        data = json.loads(response.text)
        products = data['model']['products']
        
        if response.meta["deep"] == 0:
            totalProductsCount = data['model']['totalProductsCount']
            link = response.meta["url"]
            yield Request(
                    link+str(totalProductsCount), 
                    self.parse_categories, 
                    meta={"categories":response.meta["categories"], "deep":1}, 
                    headers=self.headers,
                    dont_filter=True)
        else:

            print len(products)
            for product in products:
                try:
                    item = OrderedDict()
                    item['Vendedor'] = 547
                    item['ID'] = product['productId']
                    item['Title'] = product['displayName']
                    item['Price'] = product['salesPrice']['major'] + "." + product['salesPrice']['minor']
                    item['Currency'] = product['salesPrice']['isoCurrencySymbol']
                    item['Category URL'] = response.meta["categories"]
                    item['Details URL'] = "https://mad.coop.dk" + product['productUrl']
                    item['partner-name'] = "ccop.dk MAD"
                    item['Date'] = date.today()
                    item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')    
                    item['image_url'] = product['productDetailImageUrl']
                    
                    yield item
                except:
                    continue
