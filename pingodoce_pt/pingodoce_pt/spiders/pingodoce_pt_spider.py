# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict
from scrapy.http import TextResponse
import sys

import re, json, time, datetime

class pingodoce_pt_spiderSpider(scrapy.Spider):

    name = "pingodoce_pt_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(pingodoce_pt_spiderSpider, self).__init__(*args, **kwargs)

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

    def parse_categories(self, response):
        print response.url

        url = "https://www.pingodoce.pt/wp-content/themes/pingodoce/ajax/pd-ajax.php?action=search_results&limit=12&search_type=product_search&post_type=product&product_settings=marca-propria&pesquisa=&category=&categoria=&tag=&infiniteres=true&offsets=false&pagina=1"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        yield Request(
            url, self.parse_products,
            headers=headers,
            meta={"categories":response.meta['categories'], "url":url}
        )

###########################################################
    def parse_products(self, response):

        data = json.loads(response.text)
        raw = data['rendered_elements']
        print raw[:200]
        
        dom_data = TextResponse(url='', body=raw, encoding='utf-8')
        
        products = dom_data.xpath('//*[@class="product-item"]')
        
        print len(products)

        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 555
            item['ID'] = ''.join(product.xpath('.//article/@id').extract()).replace("post-","")
            item['Title'] = product.xpath('.//*[@class="product-box-title"]/@title').extract_first()

            item['Price'] = ''.join(product.xpath('.//*[@class="price"]/text()').re('[\d.,]+'))
            item['Currency'] = 'EURO'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = product.xpath('.//*[@class="product-box-image"]/img/@src').extract_first()
            item['partner-name'] = "pingo doce"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
#            temp_image = products.xpath('.//[contains(@style, "background-image")]/@style').re('url\(\"(https.*)\"\);')
            temp_image = product.xpath('.//*[@class="product-box-image"]/img/@src').extract_first()
            
            item['image_url'] = temp_image if temp_image else ""
            
            yield item

        if len(products):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            next_page = int(response.meta['url'].split('=')[-1])
            url = "=".join(response.meta['url'].split('=')[:-1]) + "=" + str(next_page+1)
            print url
            yield Request(
                url, self.parse_products,
                headers=headers,
                meta={"categories":response.meta['categories'], "url":url}
            )