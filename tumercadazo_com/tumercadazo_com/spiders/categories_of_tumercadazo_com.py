import scrapy, json
from urlparse import urlparse

class CategoriesOftumercadazo_com(scrapy.Spider):

	name = "categories_of_tumercadazo_com"
	start_urls = ('https://www.tumercadazo.com/',)

	use_selenium = False
	def parse(self, response):
		categories =response.xpath('//*[@id="mainNav"]/li[1]/div/ul/li/div/div/div[1]/ul/li/a/@href').extract()
		print len(categories)
		
		yield {'links':list(x for x in categories)}
