import scrapy, json
from urlparse import urlparse
from scrapy import Request, FormRequest

class CategoriesOftesco_com(scrapy.Spider):

	name = "categories_of_tesco_com"
	start_urls = ('https://www.tesco.com/groceries/en-GB/',)

	use_selenium = False
	def parse(self, response):
		csrf = response.xpath('//input[@name="_csrf"]/@value').extract_first()
		print csrf
		headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
			'x-requested-with': 'XMLHttpRequest',
			'x-csrf-token': csrf,
			'ADRUM: isAjax': True,
			'Content-Type': 'application/json',
			'Sec-Fetch-Mode': 'cors'
		}

		formdata = {}
		formdata["resources"] = [
			{
				"type":"taxonomy",
				"hash": "2021582090280711",
				"params":{
					"includeChildren": True
				}
			}
		]

		yield Request(
			"https://www.tesco.com/groceries/en-GB/resources",
			 callback=self.parse_categories, 
			 body=json.dumps(formdata), 
			 method="POST", headers=headers)

	def parse_categories(self, response):
		data = json.loads(response.text)
		categories1 = data['taxonomy']
		links = []
		for cate1 in categories1:
			if "children" not in cate1.keys():
				continue
			categories2 = cate1['children']
			for cate2 in categories2:
				if "children" not in cate2.keys():
					continue
				categories3 = cate2['children']
				for cate3 in categories3:
					if "url" not in cate3.keys():
						continue 
					if "/all" in cate3['url']:
						continue
					links.append(cate3['url'])

		# categories = response.xpath('//*[@class="menu menu-superdepartment"]/ul/li')
		# print len(categories)
		# for cate in categories:

		
		yield {'links':list(x for x in links)}
