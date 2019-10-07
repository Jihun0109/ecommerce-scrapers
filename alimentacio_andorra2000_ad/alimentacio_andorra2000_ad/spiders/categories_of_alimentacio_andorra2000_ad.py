import scrapy, json
from urlparse import urlparse

class CategoriesOfalimentacio_andorra2000_ad(scrapy.Spider):

	name = "categories_of_alimentacio_andorra2000_ad"
	start_urls = ('https://alimentacio.andorra2000.ad/',)

	use_selenium = False
	def parse(self, response):
		categories =response.xpath('//*[contains(@id, "main-menu-")]/ul/li/div/ul/li/a/@href').extract()
		print len(categories)
		yield {'links':list(x for x in categories)}
