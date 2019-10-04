# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class alsuper_do_spiderSpider(scrapy.Spider):

    name = "alsuper_do_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(alsuper_do_spiderSpider, self).__init__(*args, **kwargs)

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
            link = "https://alsuper.do" + url
            yield Request(link, self.parse_categories, meta={"categories":link})

###########################################################
    def parse_categories(self, response):
        products = response.xpath('//*[@class="item-card"]')
        print len(products)
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 558
            item['ID'] = product.xpath('.//select/@data-key_id').extract_first()
            item['Title'] = product.xpath('.//*[@class="item-title"]/text()').extract_first()
            item['Price'] = product.xpath('.//*[@class="item-price"]/text()').extract_first().replace("RD$","").strip()
            item['Currency'] = 'RD$'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = "https://alsuper.do" + product.xpath('.//*[@class="item-title"]/@href').extract_first()
            item['partner-name'] = "alsuper.do"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
#            temp_image = products.xpath('.//[contains(@style, "background-image")]/@style').re('url\(\"(https.*)\"\);')
            temp_image = product.xpath('.//*[@data-lazy]/@data-lazy').extract_first()
            if temp_image:
                temp_image = temp_image.replace("thumbs","m")

            item['image_url'] = temp_image if temp_image else ""
            
            yield item

        next_url = response.xpath('//li[@class="page-item  "]//*[@class="fas fa-angle-right"]/ancestor::a[@href]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse_categories, meta={"categories":response.meta["categories"]})