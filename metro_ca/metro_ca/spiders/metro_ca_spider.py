# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime
from scrapy.utils.response import open_in_browser

class metro_ca_spiderSpider(scrapy.Spider):

    name = "metro_ca_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(metro_ca_spiderSpider, self).__init__(*args, **kwargs)

        # f = open("categories_of_metro_ca.csv", 'r')
        # data = f.read()
        # f.close()
        # links = data.strip("\n").strip().split(',')
        # self.start_urls = [l.split("\"")[-1].strip("\"").strip() for l in links]
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
            yield Request("https://www.metro.ca"+url, self.parse_categories, meta={"categories":url})
            

###########################################################
    def parse_categories(self, response):
        
        products = response.xpath('//*[@class="product-tile item-addToCart"]')
        print len(products)
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 546
            item['ID'] = product.xpath('./@data-product-code').extract_first()
            item['Title'] = product.xpath('./@data-product-name').extract_first()
            item['Price'] = ''.join(product.xpath('.//*[contains(@class,"pi--price price-update")][1]/text()').re(r'[\d,.]+'))
            item['Currency'] = 'USD'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = response.urljoin(product.xpath('.//*[@class="pt--image product-details-link"]/@href').extract_first())
            item['partner-name'] = "Metro"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            image = product.xpath('.//*[@class="pt--image product-details-link"]/picture/img/@srcset').extract_first()
            item['image_url'] = image.split(', ')[-1].split()[0] if image else ""
            
            yield item

        next_url = response.xpath('//*[@aria-label="Next"]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse_categories, meta={"categories":response.meta["categories"]})