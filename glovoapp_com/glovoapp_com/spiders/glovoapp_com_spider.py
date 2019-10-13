# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict

import re, json, time, datetime

class glovoapp_com_spiderSpider(scrapy.Spider):

    name = "glovoapp_com_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(glovoapp_com_spiderSpider, self).__init__(*args, **kwargs)

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
        for category in self.start_urls:
            print category
            # Bue/365-bue/600/365*Kioscos*Argentinos/KIOSCOYBEBIDAS_LATAM/17148/30392
            link = "https://glovoapp.com/en/{}/store/{}".format(category.split("/")[0], category.split("/")[1])
            yield Request(
                        link, self.parse_categories, 
                        meta={"categories":category, "collections":[]}
                        )

###########################################################
    def parse_categories(self, response):
        big_collections = response.xpath('//*[@class="collection-group-list"]/section/section')
        if big_collections:
            for big_col in big_collections:
                print "BIG <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
                name = big_col.xpath('./div[last()]/text()').extract_first()
                link =big_col.xpath('./a/@href').extract_first()
                
                yield Request(
                    response.urljoin(link),
                    self.parse_bigcategories,
                    meta={"categories":response.meta['categories'], "collections":[name]}
                )
        else:
            collection_id = re.findall(r'storeCollections:\{\"(\d+)', response.body)
            print collection_id
            if collection_id:
                storeId = response.meta['categories'].split('/')[-2]
                addressId = response.meta['categories'].split('/')[-1]
                cityCode = response.meta['categories'].split('/')[0]
                headers = {
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
                    'Glovo-API-Version': '13',
                    'Glovo-App-Platform': 'web',
                    'Glovo-App-Type': 'customer',
                    'Glovo-App-Version': '7',
                    'Glovo-Device-Id': '70993541',
                    'Glovo-Language-Code': 'en',
                    'Glovo-Location-City-Code': cityCode.title(),
                }

                url = "https://api.glovoapp.com/v3/stores/{}/addresses/{}/collections/{}".format(storeId,addressId,collection_id[0])
                
                yield Request(
                    url,
                    self.parse_products,
                    headers=headers,
                    meta={"categories":response.meta['categories'], "collections":[]}
                )

            
    def parse_bigcategories(self, response):

        small_collections = response.xpath('//*[@class="collection-section"]')
        for small_col in small_collections:
            name = small_col.xpath('./div/h3/text()').extract_first()
            link = small_col.xpath('./div/a/@href').extract_first()
            print "SMALL <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<", link
            collection_id = link.split("/")[-1]

            # if collection_id != '8348431':
            #     continue

            storeId = response.meta['categories'].split('/')[-2]
            addressId = response.meta['categories'].split('/')[-1]
            cityCode = response.meta['categories'].split('/')[0]
            headers = {
				'Accept': 'application/json',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
				'Glovo-API-Version': '13',
				'Glovo-App-Platform': 'web',
				'Glovo-App-Type': 'customer',
				'Glovo-App-Version': '7',
				'Glovo-Device-Id': '70993541',
				'Glovo-Language-Code': 'en',
				'Glovo-Location-City-Code': cityCode.title(),
			}

            url = "https://api.glovoapp.com/v3/stores/{}/addresses/{}/collections/{}".format(storeId,addressId,collection_id)
            
            collections = response.meta['collections']
            yield Request(
                url,
                self.parse_products,
                headers=headers,
                meta={"categories":response.meta['categories'], "collections":collections+[name]}
            )

            

    def parse_products(self, response):
        data = json.loads(response.body)
        sections = data['sections']
        for section in sections:
            products = section['products']
            print len(products)
            # Bue/365-bue/600/365*Kioscos*Argentinos/KIOSCOYBEBIDAS_LATAM/17148/30392
            for product in products:
                item = OrderedDict()
                item['Vendedor'] = response.meta['categories'].split('/')[2]
                item['ID'] = product['id']
                item['Title'] = product['name']
                item['Price'] = product['price']
                item['Currency'] = 'ARS'
                item['Category URL'] = response.meta["categories"]
                item['Details URL'] = product['imageUrl']
                item['partner-name'] = "Glovo"
                item['Date'] = date.today()
                item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                item['image_url'] = product['imageUrl']
                if not item['image_url'] and product['imageId']:
                    item['image_url'] = "https://res.cloudinary.com/glovoapp/w_340,h_170,c_fit,f_auto,q_auto/" + product['imageId']
                if not item['Details URL']:
                    item['Details URL'] = item['image_url']
                if response.meta['collections']:
                    item['breadcumb'] = ' > '.join(response.meta['collections'])
                    if section['name']:
                        item['breadcumb'] = item['breadcumb'] + " > " + section['name']
                else:
                    item['breadcumb'] = section['name']

                yield item
        