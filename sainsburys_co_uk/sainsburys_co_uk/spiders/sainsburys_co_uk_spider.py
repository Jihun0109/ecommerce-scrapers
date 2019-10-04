# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class sainsburys_co_uk_spiderSpider(scrapy.Spider):

    name = "sainsburys_co_uk_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(sainsburys_co_uk_spiderSpider, self).__init__(*args, **kwargs)

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
        products = response.xpath('//*[@class="gridItem"]')
        print len(products)        
        
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 556
            item['ID'] = product.xpath('./div[1]/*[@class="addToTrolleytabBox"]//form/input[@name="SKU_ID"]/@value').extract_first()
            item['Title'] = product.xpath('.//h3/a/text()').extract_first().strip()
            price = product.xpath('./div[1]/*[@class="addToTrolleytabBox"]//*[@class="pricePerUnit"]/text()').re(r'[\d.,]+')
            item['Price'] = ''.join(price) if price else ""
            
            item['Currency'] = 'EURO'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = product.xpath('.//h3/a/@href').extract_first()
            item['partner-name'] = "Sainsbury's"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
#            temp_image = products.xpath('.//[contains(@style, "background-image")]/@style').re('url\(\"(https.*)\"\);')
            temp_image = product.xpath('.//h3//img/@src').extract_first()
            
            item['image_url'] = response.urljoin(temp_image) if temp_image else ""
            
            yield item

        next_url = response.xpath('//*[@class="next"]/a/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse_categories, meta={"categories":response.meta["categories"]})