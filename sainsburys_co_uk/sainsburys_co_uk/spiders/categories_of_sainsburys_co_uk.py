import scrapy, json
from urlparse import urlparse
from scrapy import Request, FormRequest

class CategoriesOfsainsburys_co_uk(scrapy.Spider):

	name = "categories_of_sainsburys_co_uk"
	start_urls = ('https://www.sainsburys.co.uk/shop/AjaxGetImmutableZDASView?requesttype=ajax&storeId=10151&langId=44&catalogId=10241&slot=',)

	use_selenium = False
	def parse(self, response):
		data = json.loads(response.text)
		items = data["navList"]
		print len(items)
		links = []

		for item in items:
			leaf = True
			for target in items:
				if item['id'] == target['id']:
					continue
				if item['id'] == target['parentId']:
					leaf = False
					break
			if leaf:
				if "special-offers" not in item['itemUrl'] and "All " not in item['name']:
					#print item['itemUrl']
					links.append(item['itemUrl'])

		yield {'links':list(x for x in links)}
