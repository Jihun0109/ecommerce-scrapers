import scrapy, json
from urlparse import urlparse
from scrapy import Request

class CategoriesOfalsuper_do(scrapy.Spider):

	name = "categories_of_glovoapp_com"
	start_urls = ('https://glovoapp.com/en/',)

	use_selenium = False
	city_codes = {
		'Bue':600,
		'Bcn':601,
		'Par':602,
	}

	buf = {}

	def start_requests(self):
		for city in self.city_codes.keys():
			self.buf[city] = []
			yield Request(
				self.start_urls[0] + city,
				meta={'city_code':city, 'vendor_id':self.city_codes[city]}
			)

	def parse(self, response):
		characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
		
		for c in characters:
			url = "https://api.glovoapp.com/v3/stores/search?query={}&type=Global".format(c)

			headers = {
				'Accept': 'application/json',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
				'Glovo-Device-Id': '70993541',
				'Glovo-API-Version': '13',
				'Glovo-App-Platform': 'web',
				'Glovo-App-Type': 'customer',
				'Glovo-App-Version': '7',
				'Glovo-Device-Id': '70993541',
				'Glovo-Language-Code': 'en',
				'Glovo-Location-City-Code': response.meta['city_code'].title(),
			}

			yield Request(url, 
							self.parse_search, 
							headers=headers, 
							meta={'city_code':response.meta.get('city_code'), 'vendor_id':response.meta.get('vendor_id')},
							dont_filter=True)
		
			
	def parse_search(self, response):
		data = json.loads(response.body)
		print len(data['results'])
		city = response.meta['city_code']
		vendor_id = response.meta['vendor_id']
		for store in data['results']:
			store_id = store['store']['id']
			if store_id in self.buf[city]:
				continue
			self.buf[city].append(store_id)
			store_path = store['store']['slug']
			store_name = store['store']['name']
			store_category = store['store']['category']
			store_addressId = store['store']['addressId']
			category = city + "/" + store_path + "/" + str(vendor_id) + "/" + store_name.replace(' ','*') + "/" + store_category.replace(' ','*') + "/" + str(store_id) + "/" + str(store_addressId)
			yield {'links': category}

