# -*- coding: utf-8 -*-
import scrapy

from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict
from scrapy.utils.response import open_in_browser

import re, json, time, datetime

class carrefour_it_spiderSpider(scrapy.Spider):

    name = "carrefour_it_spider"

    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(carrefour_it_spiderSpider, self).__init__(*args, **kwargs)

        if not categories:
            raise CloseSpider('Received no categories!')
        else:
            self.categories = categories
        self.start_urls = loads(self.categories).keys()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
            'x-dtpc': '5$248716747_592h5vPDMFEPOOINHMQEEMLKJBOPEMHQKCBBIN',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }

###########################################################

    def start_requests(self):
        hdrs = {
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
        for url in self.start_urls:
            link = "https://www.carrefour.it" + url
            yield Request(link, self.parse_categories, meta={"categories":url}, headers=hdrs)

###########################################################
    def parse_categories(self, response):

        url = "https://www.carrefour.it/api/search/availableproducts"
        url1 = "https://www.carrefour.it/api/search/availableproductsnofood"
        filtri_categoria = response.xpath('//*[@class="filtri-categoria"]/@data-filters').re(r'C4_FECategoryL3_Facet=(.*)]')
        print filtri_categoria
        if not filtri_categoria:
            return
        # |Agrumi|Albicocche|Altra frutta|Frutta esotica|Frutta in scatola e sciroppata|Frutta secca|Mele|Pere|Pesche
        formdata = {
            "IncludeFacets": True,
            "ItemsPerPage": 2000,
            "PageIndex": 1,
            "ShowCampagnaMarkers": True,
            "promoValue": None,
            "SortingParam":{
                "Direction": "desc",
                "PropertyName": "C4_SoldCounter"
            },
            "Filters":[
                {"Name": "C4_FECategoryL3_Facet", "Value":filtri_categoria[0]},
                {"Name": "C4_FECategoryL3_Facet", "Value":"*"},
                {"Name": "CategoryLevel4_Facet", "Value":"*"},
                {"Name": "C4_Brand", "Value":"*"},
                {"Name": "C4_Bio", "Value":"*"},
                {"Name": "C4_GlutenFree", "Value":"*"},
                {"Name": "C4_Kosher", "Value":"*"},
                {"Name": "C4_LactoseFree", "Value":"*"},
                {"Name": "C4_Vegan", "Value": "*"},
                {"Name": "C4_Vegetarian", "Value": "*"},
                {"Name": "C4_Halal", "Value": "*"},
                {"Name": "C4_BassoIndiceGlicemico", "Value": "*"},
                {"Name": "C4_SenzaZucchero", "Value": "*"}
            ]
        }

        yield Request(url, self.parse_category, body=json.dumps(formdata), headers=self.headers, method="POST", meta={"categories":response.meta["categories"]})
        yield Request(url1, self.parse_category, body=json.dumps(formdata), headers=self.headers, method="POST", meta={"categories":response.meta["categories"]})
    
    def parse_category(self, response):
        data = json.loads(response.text)
        products = data['Documents']
        print data["TotalCount"]
        
        print(len(products))
        
        for product in products:
            item = OrderedDict()
            item['Vendedor'] = 553
            item['ID'] = product["ProductId"]
            item['Title'] = product["PropertyBag"]["C4_Description"]
            item['Price'] = product["PropertyBag"]["CurrentPrice"]
            item['Currency'] = 'UERO'
            item['Category URL'] = response.meta["categories"]
            item['Details URL'] = "https://www.carrefour.it/dettaglio-prodotto?id="+product["ProductId"]
            item['partner-name'] = "Carrefour Italy"
            item['Date'] = date.today()
            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            item['image_url'] = product["PropertyBag"]["C4_PublicImageUrl"]
            
            yield item
