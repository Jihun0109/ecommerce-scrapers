import scrapy, json
from urlparse import urlparse

class CategoriesOfcarrefour_fr(scrapy.Spider):

	name = "categories_of_carrefour_fr"
	start_urls = ('https://www.carrefour.fr/',)

	use_selenium = False
	def start_requests(self):
		headers = {
			'upgrade-insecure-requests': '1',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
		}

		yield scrapy.Request(self.start_urls[0], headers=headers)

	def parse(self, response):
		links = []

		data = response.text.split(':navigation="')[-1].split(':store')[0].strip().strip('"')
		data = data.replace("&quot;",'"')
		nav_data = json.loads(data)
		
		food = nav_data["food"]["tree"]
		for f in food:
			if f["children"]:
				for c1 in f["children"]:
					if c1["children"]:
						for c2 in c1["children"]:
							links.append(c2["link"]["uri"])
					else:
						links.append(c1["link"]["uri"])
			else:
				links.append(f["link"]["uri"])

		print "=="
		maison = nav_data["category"]["tree"]
		for f in maison:
			if f["children"]:
				for c1 in f["children"]:
					if c1["children"]:
						for c2 in c1["children"]:
							links.append(c2["link"]["uri"])
					else:
						links.append(c1["link"]["uri"])
			else:
				links.append(f["link"]["uri"])

		
		yield {'links':list(x for x in links)}
