# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class lacolonia_com_spiderSpider(scrapy.Spider):

    name = "lacolonia_com_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(lacolonia_com_spiderSpider, self).__init__(*args, **kwargs)

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
            link = "https://www.lacolonia.com" + url
            yield Request(link, self.parse_categories, meta={"categories":url})

###########################################################
    def parse_categories(self, response):
        page_link = response.urljoin(re.findall(r'\.load\(\'(.+)\'', response.text)[0])
        
        yield Request(
            page_link + "1",
            self.parse_category,
            meta={"categories":response.meta["categories"], "pg":1, "url":page_link}
        )

    def parse_category(self, response):

        products = response.xpath('//li[@layout]')
        print len(products)

        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 552
            item['ID'] = product.xpath('.//h2/@data-id').extract_first()
            item['Title'] = product.xpath('.//h2/a/@title').extract_first()
            price = product.xpath('.//*[contains(@class, "mejorPrecio")]/text()').re(r'\d+[\d,.]+')
            if not price:
                continue
            item['Price'] = price[0]
            item['Currency'] = 'HNL'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = product.xpath('.//h2/a/@href').extract_first()
            item['partner-name'] = "La Colonia"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            temp_image = product.xpath('.//img[@id]/@src').extract_first()

            item['image_url'] = temp_image if temp_image else ""
            
            yield item

        if len(products):
            pg = response.meta['pg'] + 1
            page_link = response.meta['url']
            yield Request(                
                page_link + str(pg),
                self.parse_category,
                meta={"categories":response.meta["categories"], "pg":pg, "url":page_link}
            )
