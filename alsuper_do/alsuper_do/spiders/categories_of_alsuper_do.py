import scrapy, json
from urlparse import urlparse

class CategoriesOfalsuper_do(scrapy.Spider):

	name = "categories_of_alsuper_do"
	start_urls = ('https://alsuper.do/site/home',)

	use_selenium = False
	def parse(self, response):
		categories =response.xpath('//*[@class="navbar-nav mr-menu"]/li[2]/div/a/@href').extract()
		
		yield {'links':list(x for x in categories)}
