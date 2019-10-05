import scrapy, json
from urlparse import urlparse

class CategoriesOfeleclerc_com(scrapy.Spider):

	name = "categories_of_eleclerc_com"
	start_urls = ('http://www.e-leclerc.com/catalogue/liste',)

	use_selenium = False
	def parse(self, response):
		categories =response.xpath('//*[contains(text(), "Nos rayons")]/ancestor::div[1]/ul/li/a/@href').extract()
		
		yield {'links':list(x for x in categories)}
