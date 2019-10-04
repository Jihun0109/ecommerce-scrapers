import scrapy, json
from urlparse import urlparse

class CategoriesOfalsuper_do(scrapy.Spider):

	name = "categories_of_pingodoce_pt"
	start_urls = ('https://www.pingodoce.pt/produtos/marca/pingo-doce/',)

	use_selenium = False
	def parse(self, response):
		#categories =response.xpath('//*[@class="navbar-nav mr-menu"]/li[2]/div/a/@href').extract()
		
		yield {'links':list(['https://www.pingodoce.pt/produtos/marca/pingo-doce/'])}
