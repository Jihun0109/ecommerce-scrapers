# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict
import re, json, time, datetime

class tumercadazo_com_spiderSpider(scrapy.Spider):

    name = "tumercadazo_com_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(tumercadazo_com_spiderSpider, self).__init__(*args, **kwargs)

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
        products = response.xpath('//*[@class="container main-content"]/div[2]//*[@class="container-fluid item-list no-padding"]')
        print len(products)
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 542
            item['ID'] = ''.join(product.xpath('./div[1]/div[1]/a/@href').extract()).split("_")[-1]
            item['Title'] = product.xpath('./div[1]/div[1]/a/@title').extract_first()
            price = product.xpath('./div[2]/div[2]/*[@class="txtPrecio"]/text()').extract_first()
            if not price:
                print "price err"
                continue
            item['Price'] = price.replace("Bs. ","")

            item['Currency'] = 'BOB'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = product.xpath('./div[2]/div[2]/div[3]/a/@href').extract_first()
            item['partner-name'] = "TUMERCADAZO.COM"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            item['image_url'] = product.xpath('./div[1]/div[1]/a/img/@src').extract_first()
            
            yield item

        next_url = response.xpath('//*[text()=">"]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse_categories, meta={"categories":response.meta["categories"]})