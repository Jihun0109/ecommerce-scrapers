# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class delhaize_be_spiderSpider(scrapy.Spider):

    name = "delhaize_be_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(delhaize_be_spiderSpider, self).__init__(*args, **kwargs)

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
            link = "https://www.delhaize.be/" + url
            yield Request(link, self.parse_categories, meta={"categories":url})

###########################################################
    def parse_categories(self, response):
        products = response.xpath('//*[@class="pageBody-content"]/ul/li/div')
        print len(products)
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 545
            item['ID'] = product.xpath('./@data-item-id').extract_first()
            item['Title'] = ''.join(product.xpath('.//header/a/div/p[@class="ellipsis"]/text()').extract()).replace("\n","").strip()
            price = product.xpath('.//*[contains(@class,"property--price")]//text()').re(r'[\d,.]+')
            if not price:
                continue
            item['Price'] = price[0].replace(",",".")
            item['Currency'] = 'EURO'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = response.urljoin(product.xpath('.//header/a/@href').extract_first())
            item['partner-name'] = "DELHAIZE"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            item['image_url'] = response.urljoin(product.xpath('.//*[@class="layout-shot"]/a/img/@src').extract_first())
            
            yield item

        next_url = response.xpath('//*[@class="next-page pagination-button active-item"]/a/@href').extract()
        if next_url:
            yield Request(response.urljoin(next_url[0]), self.parse_categories, meta={"categories":response.meta["categories"]})