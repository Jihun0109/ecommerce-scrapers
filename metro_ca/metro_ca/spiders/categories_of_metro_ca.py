import scrapy, json
from urlparse import urlparse
from scrapy.utils.response import open_in_browser

class CategoriesOfmetro_ca(scrapy.Spider):

	name = "categories_of_metro_ca"
	start_urls = ('https://www.metro.ca/en/online-grocery/search',)

	use_selenium = False
	def parse(self, response):
		#open_in_browser(response)
		categories =response.xpath('//*[@class="lm--sub-cat-list"]/li/a/@href').extract()
		yield {'links':list(x for x in categories)}
