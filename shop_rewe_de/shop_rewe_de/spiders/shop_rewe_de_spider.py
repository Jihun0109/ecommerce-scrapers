# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class shop_rewe_de_spiderSpider(scrapy.Spider):

    name = "shop_rewe_de_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(shop_rewe_de_spiderSpider, self).__init__(*args, **kwargs)

        if not categories:
            raise CloseSpider('Received no categories!')
        else:
            self.categories = categories
        self.start_urls = loads(self.categories).keys()

        self.headers = {
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            ':scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9'
        }
###########################################################

    def start_requests(self):
        for url in self.start_urls:
            link = "https://shop.rewe.de" + url
            yield Request(
                link, 
                self.parse_categories, 
                meta={"categories":url}, 
                headers=self.headers
                )

###########################################################
    def parse_categories(self, response):
        products = response.xpath('//*[@class="search-service-rsTilesDefault"]/div')
        print len(products)
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 543
            item['ID'] = product.xpath('./div[1]/input/@value').extract_first()
            item['Title'] = product.xpath('.//*[@class="LinesEllipsis  "]/text()').extract_first()
            price = product.xpath('.//*[@class="search-service-productOfferPrice"]/text()').re(r'[\d.,]+')
            if not price:
                price = product.xpath('.//*[@class="search-service-productPrice"]/text()').re(r'[\d.,]+')
                if not price:
                    continue

            item['Price'] = price[0].replace(",",".")

            item['Currency'] = 'EURO'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = "https://shop.rewe.de" + product.xpath('./div[2]/a/@href').extract_first()
            item['partner-name'] = "REWE DEIN MARKT"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            item['image_url'] = product.xpath('./div[2]/a//img/@src').extract_first()
            item['image_url'] = item['image_url'].split("?")[0]
            yield item

        next_url = response.xpath('//*[@class="search-service-paginationArrow search-service-paginationArrowEnabled search-service-paginationArrowBack"]/@href').extract_first()
        if next_url:
            yield Request(
                    response.urljoin(next_url), 
                    self.parse_categories, 
                    meta={"categories":response.meta["categories"]}, 
                    headers=self.headers
                    )