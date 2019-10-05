# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class eleclerc_com_spiderSpider(scrapy.Spider):

    name = "eleclerc_com_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(eleclerc_com_spiderSpider, self).__init__(*args, **kwargs)

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
            link = "http://www.e-leclerc.com" + url
            yield Request(link, self.parse_categories, meta={"categories":url})

###########################################################
    def parse_categories(self, response):
        code = response.xpath('//script[contains(text(), "templateNational ")]/text()').re(r'univers : \'([a-zA-Z0-9]+)\'')
        if not code:
            return
        
        maxResult = 1000
        url = "http://www.e-leclerc.com/produit/mea/liste?choixProduits=operationsActives&codeSousUnivers=&codeUnivers={}&codesEanProduits=&codesOperations=&maxResults={}&sousUnivers=&triParOrdreDeContribution=&typeProduits=tous&typeUnivers=rayon&univers={}".format(code[0],maxResult,code[0])

        yield Request(url, self.parse_products, meta={"categories":response.meta["categories"]})

    def parse_products(self, response):
        products = re.findall(r'[0-9]+',response.text)        
        print len(products)

        for pid in products:
            url = "http://www.e-leclerc.com/produit/fragment/mea/{}".format(pid)
            yield Request(url, self.parse_product, meta={"categories":response.meta["categories"], "pid":pid})


    def parse_product(self, response):
        item = OrderedDict()
        item['Vendedor'] = 549
        item['ID'] = response.meta['pid']
        item['Title'] = response.xpath('.//*[@class="box-item-title"]/a/text()').extract_first()
        price = re.findall(r'\$prix=([\d.,]+)', response.text)
        if not price:
            return
        item['Price'] = ''.join(price).replace(',','.')
        item['Currency'] = 'EURO'
        item['Category URL'] = response.meta["categories"]
        item['Details URL'] = response.url

        item['partner-name'] = "E.Leclerc"
        item['Date'] = date.today()
        item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        temp_image = response.xpath('.//*[@class="img-responsive"]/@src').extract_first()

        item['image_url'] = temp_image if temp_image else ""
        
        yield item