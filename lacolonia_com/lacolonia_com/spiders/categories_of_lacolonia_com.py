import scrapy, json
from urlparse import urlparse

class CategoriesOflacolonia_com(scrapy.Spider):

	name = "categories_of_lacolonia_com"
	start_urls = ('https://www.lacolonia.com/',)

	use_selenium = False
	def parse(self, response):
		
		categories =response.xpath('//a[@class="linkMenu"]/following-sibling::ul[1]//li/a/@href').extract()
		
		yield {'links':list(x for x in categories)}
