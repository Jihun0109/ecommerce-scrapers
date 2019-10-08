import scrapy, json
from urlparse import urlparse

class CategoriesOfshop_rewe_de(scrapy.Spider):

	name = "categories_of_shop_rewe_de"
	start_urls = ('https://shop.rewe.de/',)

	headers = {
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-site': 'same-origin',
		'sec-fetch-user': '?1',
		':scheme': 'https',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'en-US,en;q=0.9'
	}
	def start_requests(self):
		for url in self.start_urls:
			yield scrapy.Request(
				url,
				self.parse,
				headers=self.headers
			)
	def parse(self, response):
		categories =response.xpath('//*[@id="rs-primary-navigation"]/li[2]/ul/li/a/@href').extract()
		print len(categories)
		
		yield {'links':list(x for x in categories)}
