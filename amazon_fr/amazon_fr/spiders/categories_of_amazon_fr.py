import scrapy, json
from urlparse import urlparse

class CategoriesOfamazon_fr(scrapy.Spider):

	name = "categories_of_amazon_fr"
	start_urls = ('https://www.amazon.fr/gp/site-directory?ref_=nav_em_T1_0_2_2_22__fullstore',)

	custom_settings = {
		"CONCURRENT_REQUESTS":1,
		"CONCURRENT_REQUESTS_PER_DOMAIN":1,
		"CONCURRENT_REQUESTS_PER_IP":1,
		"DOWNLOAD_DELAY":5
	}

	use_selenium = False
	def parse(self, response):
		big_categories =response.xpath('//*[@class="popover-grouping"]')
		print len(big_categories)
		links = []
		black_list = ["Video", "Music","Liseuses Kindle", "Tablettes Fire", "Appstore pour Android", "Livres et Audible", "Musique", "Echo et Alexa", "Amazon Fire TV", "Business"]
		for big_cate in big_categories:
			big_title = ''.join(big_cate.xpath('./h2/text()').extract())
			disabled = False
			for bl in black_list:
				if bl in big_title:
					disabled = True
					break
			if disabled:
				continue			

			categories = big_cate.xpath('./ul/li/a')
			for cate in categories:
				title = ''.join(cate.xpath('./text()').extract())
				if "Tous les" in title or "Toute" in title:
					continue
				link = cate.xpath('./@href').extract_first()
				links.append(link)

		yield {'links':list(x for x in links)}
