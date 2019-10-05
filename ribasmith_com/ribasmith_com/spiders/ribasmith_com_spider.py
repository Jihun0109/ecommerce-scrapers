# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class ribasmith_com_spiderSpider(scrapy.Spider):

    name = "ribasmith_com_spider"

    use_selenium = False
    start_urls = ['https://www.ribasmith.com/',]
    category_urls = []
    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(ribasmith_com_spiderSpider, self).__init__(*args, **kwargs)

        if not categories:
            raise CloseSpider('Received no categories!')
        else:
            self.categories = categories
        self.category_urls = loads(self.categories).keys()

        # self.headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'
        # }

###########################################################

    def parse(self, response):
        for url in self.category_urls:
            yield Request(url, self.parse_categories, meta={"categories":url})

###########################################################
    def parse_categories(self, response):
        products = response.xpath('//*[@class="item product product-item"]//*[@class="product-item-info"]')
        print len(products)
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 554
            item['ID'] = product.xpath('.//input[@name="product"]/@value').extract_first()
            item['Title'] = product.xpath('.//div[1]/a[1]/img/@alt').extract_first()
            item['Price'] = product.xpath('.//*[contains(@id, "product-price-")]/@data-price-amount').extract_first()
            item['Currency'] = 'USD'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = response.xpath('.//div[1]/a[1]/@href').extract_first()
            item['partner-name'] = "Riba Smith"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            temp_image = product.xpath('.//div[1]/a[1]/img/@src').extract_first()
            item['image_url'] = temp_image if temp_image else ""
            
            yield item

        next_url = response.xpath('//*[@class="action  next"]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse_categories, meta={"categories":response.meta["categories"]})