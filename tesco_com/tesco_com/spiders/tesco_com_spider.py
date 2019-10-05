# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class tesco_com_spiderSpider(scrapy.Spider):

    name = "tesco_com_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(tesco_com_spiderSpider, self).__init__(*args, **kwargs)

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
            link = "https://www.tesco.com/groceries/en-GB/shop" + url
            yield Request(link, self.parse_categories, meta={"categories":url})

    
###########################################################
    def parse_categories(self, response):
        products = response.xpath('//*[@class="product-list grid"]/li/div')
        print len(products)
        
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 557
            item['ID'] = product.xpath('./div[1]/div[1]/div[1]/@data-auto-id').extract_first()
            item['Title'] = product.xpath('.//h3/a/text()').extract_first()
            item['Price'] = product.xpath('.//*[@class="price-control-wrapper"]//span[@data-auto="price-value"]/text()').extract_first()
            item['Currency'] = 'EURO'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = "https://www.tesco.com" + product.xpath('.//h3/a/@href').extract_first()
            item['partner-name'] = "TESCO"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
#            temp_image = products.xpath('.//[contains(@style, "background-image")]/@style').re('url\(\"(https.*)\"\);')
            temp_image = product.xpath('.//img/@src').extract_first()
            
            item['image_url'] = temp_image if temp_image else ""
            
            yield item

        next_url = response.xpath('//*[@class="icon-icon_whitechevronright"]/ancestor::a[@class="pagination--button prev-next"]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse_categories, meta={"categories":response.meta["categories"]})