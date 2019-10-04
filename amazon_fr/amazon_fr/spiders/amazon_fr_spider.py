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

class amazon_fr_spiderSpider(scrapy.Spider):

    name = "amazon_fr_spider"

    custom_settings = {
		"CONCURRENT_REQUESTS":1,
		"CONCURRENT_REQUESTS_PER_DOMAIN":1,
		"CONCURRENT_REQUESTS_PER_IP":1,
		"DOWNLOAD_DELAY":5
	}
    use_selenium = False

    total_ids = []
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(amazon_fr_spiderSpider, self).__init__(*args, **kwargs)

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
            link = "https://www.amazon.fr" + url
            yield Request(link, self.parse_categories, meta={"categories":link})

    def parse_categories(self, response):
        headers = {
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
            }
        categories = response.xpath('//img[contains(@class, "octopus")][contains(@class, "category")]/ancestor::a[1]/@href').extract()

        if categories:
            for cate in categories:
                yield Request(
                    response.urljoin(cate),
                    self.parse_categories,
                    headers=headers,
                    meta={"categories":response.meta["categories"]}
                )
                #break
        else:
            products = response.xpath('//img[contains(@class, "-image")][contains(@class, "s")][not(contains(@class, "flyout"))][not(contains(@class, "dynamic"))][not(contains(@class, "octopus"))]/ancestor::a[1]/@href').extract()
            print len(products)
            for product in products:
                #link = "https://www.amazon.fr/SHAN-ZU-Aiguiseur-Couteaux-Aiguiser/dp/B07H7YMJL5/ref=gbps_tit_s-6_ea7f_3bc16ee1?smid=A1OL1MT0V3JV4N&pf_rd_p=78f7b771-d119-43ed-afd1-82bba8f7ea7f&pf_rd_s=slot-6&pf_rd_t=701&pf_rd_i=gb_main&pf_rd_m=A1X6FK5RDHNB96&pf_rd_r=8XJB5QMC0FAJWZQRJ2PM"
                print product

                yield Request(
                    response.urljoin(product),
                    self.parse_product,
                    meta={'categories':response.meta['categories'],},
                    headers=headers
                )

                #break

            next_link = response.xpath('//*[@class="a-last"]/a/@href').extract()
            if len(next_link) == 0:
                next_link = response.xpath('//*[@class="pagnRA"]/a/@href').extract()

            # Pagination
            if next_link:
                print next_link[0].split("_")[-1]

                yield Request(
                        response.urljoin(next_link[0]),
                        self.parse_categories, meta={"categories":response.meta['categories']},
                        headers=headers
                        )

    def parse_product(self, response):
        #open_in_browser(response)
        item = OrderedDict()

        title = ''.join(response.xpath('//meta[@name="title"]/@content').extract()).split(": Amazon.fr")[0]
        rating = response.xpath('//*[@data-feature-name="averageCustomerReviews"]//i[contains(@class, "a-icon-star")]/@class').extract_first()
        rating = rating.replace("a-icon a-icon-star a-star-","").replace("-",".")
        comments = ''.join(response.xpath('//*[@data-feature-name="averageCustomerReviews"]//*[@id="acrCustomerReviewText"]/text()').re(r'[\d.,]+'))
        asin = response.xpath('//*[@id="desktop_buybox"]//form//input[@name="ASIN"]/@value').extract_first()
        browse_node_id = response.xpath('//*[@id="desktop_buybox"]//form//input[@name="nodeID"]/@value').extract_first()
        brand = response.xpath('//*[@id="mbc"]/@data-brand').extract_first()
        breadcrumb = response.xpath('//a[@class="a-link-normal a-color-tertiary"]/text()').extract()
        descriptions = response.xpath('//*[@id="feature-bullets"]//li[not(@id)]//text()').extract()
        
        breadcrumb = [x.strip("\n").strip() for x in breadcrumb]
        images = re.findall(r'(https:\/\/[0-9a-zA-Z\_\.\-\/]*)\":\[\d+,\d+\]},\"variant\":', ''.join(response.xpath('//script[contains(text(), "trigger ATF event")]/text()').extract()))
        
        descs = response.xpath('//h2[contains(text(), "Informations sur")]/following-sibling::div[1]/div[1]//table//tr')
        descs = response.xpath('//*[text()="Descriptif technique"]/ancestor::div[1]/following-sibling::div[1]//table//tr')
        features = []
        price = ''.join(response.xpath('//*[@id="desktop_buybox"]//*[contains(@class, "a-color-price")][1]').re("[\d.,]+")).replace(",",".")

        weight = ""
        l = ""
        w = ""
        h = ""

        if len(descs):
            for desc in descs:
                k = desc.xpath('./td[1]/text()').extract_first()                
                v = desc.xpath('./td[2]/text()').extract_first()
                if "Poids de" in k:
                    weight = v

                dimension = re.findall(r'([\d.,\s]+)x([\d.,\s]+)x([\d.,\s]+)', v)
                
                if dimension:
                    l = dimension[0][0].strip()
                    w = dimension[0][1].strip()
                    h = dimension[0][2].strip()
                features.append(k+":"+v)

        item['Vendedor'] = 559
        item["product url"] = response.url
        item["title"] = title
        item["asin"] = asin
        item["ean"] = ""
        item["mpn"] = ""
        item["browse_node_id"] = browse_node_id
        item["description"] = ",".join([x.strip("\n").strip() for x in descriptions])
        item["Image url 1"] = images[0] if len(images) > 0 else ""
        item["Image url 2"] = images[1] if len(images) > 1 else ""
        item["Image url 3"] = images[2] if len(images) > 2 else ""
        item["Image url 4"] = images[3] if len(images) > 3 else ""
        item["Image url 5"] = images[4] if len(images) > 4 else ""
        item["breadcrumb"] = ">".join(breadcrumb)
        item["brand"] = brand
        item["item_length"] = l
        item["item_width"] = w
        item["item_height"] = h
        item["item_weight"] = weight
        item["package_length"] = ""
        item["package_width"] = ""
        item["package_height"] = ""
        item["package_weight"] = ""
        item["price"] = price
        item['rating'] = rating
        item["comment_nbr"] = comments
        item["Features"] = "|".join(features)
        item["Variation Attributes"] = ""
        item['Date'] = date.today()
        item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

        yield item

