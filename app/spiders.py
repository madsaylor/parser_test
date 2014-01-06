from grab.spider import Spider, Task
import logging
import csv
from collections import OrderedDict

class EdamollSpider(Spider):
	initial_urls = ['http://edamoll.ru']
	domain = 'http://edamoll.ru'

	def prepare(self):
		self.result_file = csv.writer(open('result.csv', 'w'))
		self.result_counter = 0

	def task_initial(self, grab, task):
		for s in grab.doc.select('//*[@class="item-text "]//a/@href'):
			yield Task('paginate', url=grab.config['url'] + s.text())

	def task_paginate(self, grab, task):		
		try:
			page = grab.doc.select('//div[@class="nav_top"]//div[@class="nav-pages flr"]/a[not(@class)]')[-1]
			pages_count = int(page.text())				
			page_url = self.domain + page.attr('href').split('=')[0] 
			for i in xrange(pages_count):
				yield Task('product_list', url=page_url + '=' + str(i + 1))
		except IndexError:
			yield Task('product_list', url=grab.response.url)
	
	def task_product_list(self, grab, task):
		for s in grab.doc.select('//div[@class="catalog_item"]/a/@href'):
			yield Task('product', url=self.domain + s.text())

	def task_product(self, grab, task):
		product = {
			'name' : grab.doc.select('//h3[@class="catalog-element-name"]').text(),
			'price' : float(grab.doc.select('//*[@class="item_price price"]/text()').text() + '.' + grab.doc.select('.//*[@class="decimal"]').text()),
			'image_url' : self.domain + grab.doc.select('//div[@class="catalog-element-image"]/img/@src').text()			
		}
		breadcrumbs = grab.doc.select('//ul[@class="breadcrumb-navigation"]//a')
		for i, crumb in enumerate(breadcrumbs):
			product['category'+str(i)] = crumb.text()
		result = OrderedDict(sorted(product.items(), key=lambda t: t[0]))
		self.result_file.writerow([v.encode('utf-8') for v in result.values() if not type(v) is float ])
		self.result_counter += 1

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	bot = EdamollSpider(thread_number=2)
	bot.run()