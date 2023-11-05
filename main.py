#!/usr/bin/env python3
import sys
from _decimal import Decimal

from lxml import etree

parser = etree.HTMLParser()

with open('tg-webapp/index.html', 'r') as fp:
	data = fp.read()
	# tree = etree.HTML(data)

tree = etree.parse('tg-webapp/index.html', parser)


items_catalog = dict()

for div in tree.xpath("//section[@class='cafe-page cafe-items']/./div[@data-item-id]"):
	#d = div.xpath('./div[@class="cafe-item-label"]')
	# print(div.xpath('./div/text()'))
	# title = div.xpath("//div[@class='cafe-item-label']")
	title = div.xpath(".//span[@class='cafe-item-title']/text()")[0]
	price = int(div.xpath(".//span[@class='cafe-item-price']/text()")[0].split(' ')[0])
	# print(title, price, div.attrib['data-item-id'])

	items_catalog[int(div.attrib['data-item-id'])] = {
		'title': title,
		'price': price
	}

print(repr(items_catalog))

sys.exit(0)

for div_price_attr in tree.xpath("//div[@data-item-price]"):
	val = int(div_price_attr.attrib['data-item-price'])
	new_val = val*92
	# print(val, new_val)
	data = data.replace('data-item-price="%d">' % val, 'data-item-price="%d">' % new_val, 1)
# 	# div_price_attr.attrib['data-item-price'] *= 92


sys.exit(0)
for class_price in tree.xpath("//span[@class='cafe-item-price']"):
	old_price = str(class_price.text)
	new_price = old_price.replace('$', '', 1)
	new_price = Decimal(new_price)*92
	new_price = '%d ₽' % new_price
	# print(old_price, '%d ₽' % new_price)
	data = data.replace(old_price, new_price, 1)

# result = etree.tostring(tree.getroot(), pretty_print=True, method="html")

with open('index_out.html', 'w+') as fp:
	fp.write(data)
# print(result)