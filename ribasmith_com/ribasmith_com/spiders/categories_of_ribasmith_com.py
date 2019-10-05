import scrapy, json
from urlparse import urlparse

class CategoriesOfribasmith_com(scrapy.Spider):

	name = "categories_of_ribasmith_com"
	start_urls = ('https://www.ribasmith.com/index.php/departamentos.html',)

	use_selenium = False
	def parse(self, response):
		categories =response.xpath('//*[contains(@class,"sidebar-main")]//li/a/@href').extract()
		
		yield {'links':list(x for x in categories)}
