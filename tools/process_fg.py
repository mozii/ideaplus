#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Daniel Yang on 2011-02-10.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')


from BeautifulSoup import BeautifulSoup

from pymongo import Connection
import gridfs
from twisted.internet import reactor, defer
from twisted.web.client import getPage, downloadPage

connection = Connection()
db = connection.fuguang
cup_table = db.cups
fuguang_table = db.fuguang


url_list = []

html_escape_table = {"&": "&amp;", '"': "&quot;", "'": "&apos;", ">": "&gt;", "<": "&lt;",}
def html_escape(text):
    return "".join(html_escape_table.get(c,c) for c in text)

def html_unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&amp;", "&")
    s = s.replace("&quot;", '"')
    s = s.replace("&apos;", "'")
    return s

for page in cup_table.find():
	url_list.append(page['link'])

print 'got ', len(url_list), 'pages'

# reverse it.
#url_list.reverse()


def handleError(error):
	print 'got errpr', error

def processPage(page, url):
	
	print 'processing page ', url

	soup = BeautifulSoup(page)
	
	product_name = soup.findAll('span',{'class':'style01'})[-1]
	ku1 = soup.findAll('span',{'class':'style03'})[-1]
	table = soup.find('table',{'style': 'MARGIN: 10px'})
	if not table:
		print url, 'is not ok--------'
	
	image = table.img['src']
	
	if not image:
		print url, 'is not ok--------'
	
	desc = table.p
	if not desc:
		print url, 'is not ok--------'
	
	desc = str(desc).replace('<p>', '').replace('</p>', '').replace('<br />', '|')
	
	#page = html_escape(page.decode('gb2312').encode('UTF-8'))
	already_have = fuguang_table.count()
	product = {'number':already_have+1, 'name': product_name.text, 'ku1':ku1.text, 'image':image, 'desc':desc, 'url':url, }

	print 'saved ', fuguang_table.insert(product)
	
	reactor.callLater(1, getFGPage)

def getFGPage():
	if len(url_list) == 0:
		print 'over........'
		reactor.stop()
	
	print 'remain ', len(url_list), '----------------'
	
	url = str(url_list.pop())
	
	count = fuguang_table.find({'url':url}).count()
	if count == 0:
		pageFetchedDeferred = getPage(url) 
		pageFetchedDeferred.addCallback(processPage, url)  
		pageFetchedDeferred.addErrback(handleError)
	else:
		print url, 'already exists................'
		getFGPage()
reactor.callLater(1, getFGPage)

reactor.run()
