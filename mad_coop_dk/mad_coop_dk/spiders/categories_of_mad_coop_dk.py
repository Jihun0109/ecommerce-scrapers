import scrapy, json
from urlparse import urlparse

class CategoriesOfmad_coop_dk(scrapy.Spider):

	name = "categories_of_mad_coop_dk"
	start_urls = ('https://mad.coop.dk/',)

	use_selenium = False
	def parse(self, response):
		categories =response.xpath('//*[@class="siteNav-sub"]/div[2]/ul[2]/li//ul/li/a/@href').extract()
		
		yield {'links':list(x for x in categories)}
