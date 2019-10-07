# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class tienda_consum_es_spiderSpider(scrapy.Spider):

    name = "tienda_consum_es_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(tienda_consum_es_spiderSpider, self).__init__(*args, **kwargs)

        if not categories:
            raise CloseSpider('Received no categories!')
        else:
            self.categories = categories
        self.start_urls = loads(self.categories).keys()

        self.headers = {
            'X-TOL-CHANNEL': '1',
            'X-TOL-LOCALE': 'es',
            'X-TOL-ZONE': '0',
            'Accept': 'application/json, text/plain, */*',
        }

###########################################################
 
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.parse_categories, meta={"categories":url, "deep":0}, headers=self.headers)

###########################################################
    def parse_categories(self, response):
        if response.meta["deep"] == 0:
            category_id = re.findall(r'c\-(\d+)', response.url)[0]
            url = "https://tienda.consum.es/api/rest/V1.0/catalog/product?offset=0&limit=15&orderById=7&categories={}&showFilter=true".format(category_id)

            yield Request(
                url, 
                self.parse_categories, 
                headers=self.headers, 
                meta={"categories":response.meta["categories"], "deep":1, "category_id":category_id},
                dont_filter=True
            )
        else:
            total_products = json.loads(response.text)["totalCount"]
            url = "https://tienda.consum.es/api/rest/V1.0/catalog/product?offset=0&limit={}&orderById=7&categories={}&showFilter=true".format(total_products, response.meta["category_id"])
            yield Request(
                url,
                self.parse_products,
                headers=self.headers,
                meta={"categories":response.meta["categories"]},
            )

    def parse_products(self, response):
        data = json.loads(response.text)
        products = data["products"]
        print len(products)

        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 548
            item['ID'] = product['id']
            item['Title'] = product['productData']['description']
            item['Price'] = product['priceData']['prices'][0]['value']['centAmount']
            item['Currency'] = 'EURO'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = product['productData']['url']
            item['partner-name'] = "CONSUM"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            item['image_url'] = product['productData']['imageURL']
            
            yield item
