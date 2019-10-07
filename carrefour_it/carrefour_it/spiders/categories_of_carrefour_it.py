import scrapy, json
from urlparse import urlparse

class CategoriesOfcarrefour_it(scrapy.Spider):

	name = "categories_of_carrefour_it"
	start_urls = ('https://www.carrefour.it/',)

	use_selenium = False
	def parse(self, response):
		links = []
		categories = response.xpath('//*[@class="c-treenav__branches"]/li/ul/li[position()>1][position()<last()-1]')
		for cate in categories:
			ul = cate.xpath('./ul')
			if ul:
				lis = ul.xpath('./li')
				for li in lis:
					ul_1 = li.xpath('./ul')
					if ul_1:
						links = links + ul_1.xpath('./li/a/@href').extract()
					else:
						links.append(li.xpath('./a/@href').extract_first())		
			else:
				links.append(cate.xpath('./a/@href').extract_first())
		#categories =response.xpath('//*[@class="navbar-nav mr-menu"]/li[2]/div/a/@href').extract()
		
		yield {'links':list(x for x in links)}
