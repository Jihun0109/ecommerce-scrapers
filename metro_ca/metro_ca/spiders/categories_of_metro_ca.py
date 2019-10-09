import scrapy, json
from urlparse import urlparse
from scrapy.utils.response import open_in_browser

class CategoriesOfmetro_ca(scrapy.Spider):

	name = "categories_of_metro_ca"
	start_urls = ('https://fresh2go.metro.ca/',)

	use_selenium = False
	def parse(self, response):
		
		categories =response.xpath('//*[@id="nav"]/ul/li/ul/li/a/@href').extract()
		yield {'links':list(x for x in categories)}
