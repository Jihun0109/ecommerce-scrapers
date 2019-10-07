import scrapy, json
from urlparse import urlparse
from scrapy.utils.response import open_in_browser

class CategoriesOfdelhaize_be(scrapy.Spider):

	name = "categories_of_delhaize_be"
	start_urls = ('https://www.delhaize.be/nl-be/shop',)

	use_selenium = False
	def parse(self, response):
		
		categories =response.xpath('//*[@class="LeftHandNav"]//*[@class="top-level-container"]/ul/li/div/ul/li/a/@href').extract()
		
		print len(categories)
		yield {'links':list(x for x in categories)}
