# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class alimentacio_andorra2000_ad_spiderSpider(scrapy.Spider):

    name = "alimentacio_andorra2000_ad_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(alimentacio_andorra2000_ad_spiderSpider, self).__init__(*args, **kwargs)

        if not categories:
            raise CloseSpider('Received no categories!')
        else:
            self.categories = categories
        self.start_urls = loads(self.categories).keys()

        # self.headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'
        # }

###########################################################

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.parse_categories, meta={"categories":url, "pg":1})

###########################################################
    def parse_categories(self, response):
        products = response.xpath('//*[@class="main-products product-grid"]/div/div')
        if len(products):
            for product in products:
                item = OrderedDict()
                item['Vendedor'] = 544
                id = product.xpath('./div[1]/a/@onclick').re(r'quickview\(\'(\d+)\'\)')[0]
                item['ID'] = id
                item['Title'] = product.xpath('./div[1]/a/div/img/@title').extract_first()
                prices = product.xpath('.//*[@class="price-new"]/text()').re(r'[\d.,]+')
                if not prices:
                    prices = product.xpath('.//*[@class="price-normal"]/text()').re(r'[\d.,]+')
                    if not prices:
                        continue

                item['Price'] = prices[0].replace(',','.')
                item['Currency'] = 'EURO'
                item['Category URL'] = response.meta["categories"]
                item['Details URL'] = "https://alimentacio.andorra2000.ad/index.php?route=journal3/product&product_id={}&popup=quickview".format(id)
                item['partner-name'] = "ANDORRA 2000"
                item['Date'] = date.today()
                item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                item['image_url'] = product.xpath('./div[1]/a/div/img/@src').extract_first()
                
                yield item

            pg = response.meta["pg"]+1
            url = response.meta['categories'] + "&page=" + str(pg)
            yield Request(
                url,
                self.parse_categories,
                meta={"categories":response.meta["categories"], "pg":pg}
            )