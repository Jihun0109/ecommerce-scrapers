import scrapy, json
from urlparse import urlparse
from scrapy.utils.response import open_in_browser

class CategoriesOftienda_consum_es(scrapy.Spider):

	name = "categories_of_tienda_consum_es"
	start_urls = ('http://tienda.consum.es/api/rest/V1.0/shopping/category/menu',)

	use_selenium = False

	def parse(self, response):
		links = []
		top_categories = json.loads(response.text)
		for top_cate in top_categories:
			sub_categories = top_cate["subcategories"]
			for sub_cate in sub_categories:
				sub_sub_categories = sub_cate["subcategories"]
				if len(sub_sub_categories) == 0:
					links.append(sub_cate["url"])
				else:
					for sub_sub_cate in sub_sub_categories:
						links.append(sub_sub_cate["url"])
		
		yield {'links':list(x for x in links)}
