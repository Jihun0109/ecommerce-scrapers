# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class carrefour_fr_spiderSpider(scrapy.Spider):

    name = "carrefour_fr_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(carrefour_fr_spiderSpider, self).__init__(*args, **kwargs)

        if not categories:
            raise CloseSpider('Received no categories!')
        else:
            self.categories = categories
        self.start_urls = loads(self.categories).keys()

        self.headers = {
			'upgrade-insecure-requests': '1',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
		}

###########################################################

    def start_requests(self):
        for url in self.start_urls:
            link = "https://www.carrefour.fr" + url
            yield Request(link, self.parse_categories, meta={"categories":url}, headers=self.headers)

###########################################################
    def parse_categories(self, response):
        products = response.xpath('//*[@class="product-list"]/ul/li//article')
        print len(products)
        
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 550
            item['ID'] = product.xpath('.//*[@class="add-to-shoppinglist"]/@ean').extract_first()
            item['Title'] = product.xpath('.//*[@class="ds-product-card--vertical-text"]/a/@title').extract_first()
            item['Price'] = ''.join(product.xpath('.//*[@class="product-card-price__price"]//text()').re(r'[\d.,]+')).replace(',','.')
            item['Currency'] = 'EURO'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = "https://www.carrefour.fr" + product.xpath('.//*[@class="ds-product-card--vertical-text"]/a/@href').extract_first()
            item['partner-name'] = "Carrefour France"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
#            temp_image = products.xpath('.//[contains(@style, "background-image")]/@style').re('url\(\"(https.*)\"\);')
            temp_image = product.xpath('.//*[@class="product-card-image"]/img/@data-src').extract_first()
            if not temp_image:
                temp_image = product.xpath('.//*[@class="product-card-image"]/img/@src').extract_first()
            item['image_url'] = "https://www.carrefour.fr"+temp_image if temp_image else ""
            
            yield item

        next_url = response.xpath('//*[@class="a-button button-link is-secondary"]/@href').extract()
        if next_url:
            yield Request(response.urljoin(next_url[-1]), self.parse_categories, meta={"categories":response.meta["categories"]}, headers=self.headers)