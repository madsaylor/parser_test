from grab.spider import Spider, Task
import logging
import csv

class EdamollSpider(Spider):
	initial_urls = ['http://edamoll.ru']

	def prepare(self):
		self.result_file = csv.writer(open('result.txt', 'w'))
		self.result_counter = 0

	def task_initial(self, grab, task):
		for s in grab.doc.select('//*[@class="item-text "]//a/@href'):
			yield Task('paginate', url=grab.config['url'] + s.text())

	def task_paginate(self, grab, task):
		page = grab.doc.select('//div[@class="nav_top"]//div[@class="nav-pages flr"]/a[not(@class)]')[-1]
		pages_count = int(page.text())		
		page_url = grab.config['url'] + page.attr('href').split('=')[0] 

		for i in xrange(pages_count):
			yield Task('product_list', url=page_url + '=' + str(i + 1))
	
	def task_product_list(self, grab, task):
		for s in grab.doc.select('//div[@class="catalog_item"]/a/@href'):
			yield Task('product', url=grab.config['url'] + s.text())

	def task_product(self, grab, task):
		product = {
			'name' : grab.doc.select('//h3[@class="catalog-element-name"]').text(),
			'price' : float(grab.doc.select('//*[@class="item_price price"]/text()').text() + '.' + grab.doc.select('.//*[@class="decimal"]').text()),
			'image_url' : grab.doc.select('//div[@class="catalog-element-image"]/img/@src').text()
		}
		self.result_file.writerow([
			product['name'].encode('utf-8'),
			product['price'].encode('utf-8'),
			product['image_url'].encode('utf-8')
		])
		self.result_counter += 1

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	bot = EdamollSpider(thread_number=2)
	bot.run()