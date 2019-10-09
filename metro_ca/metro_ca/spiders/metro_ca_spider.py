# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class metro_ca_spiderSpider(scrapy.Spider):

    name = "metro_ca_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(metro_ca_spiderSpider, self).__init__(*args, **kwargs)

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
            yield Request(url, self.parse_categories, meta={"categories":url})

###########################################################
    def parse_categories(self, response):
        products = response.xpath('//*[@class="category-products"]/ul/li')
        print len(products)
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 546
            item['ID'] = product.xpath('./div/span/@id').re(r'\d+')[0]
            item['Title'] = product.xpath('./a/@title').extract_first()
            item['Price'] = ''.join(product.xpath('./div/span/span/text()').extract_first()).replace("$","")
            item['Currency'] = 'USD'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = product.xpath('./a/@href').extract_first()
            item['partner-name'] = "Metro"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            item['image_url'] = product.xpath('./a/img/@src').extract_first()
            
            yield item

        next_url = response.xpath('//*[@class="next i-next"]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse_categories, meta={"categories":response.meta["categories"]})