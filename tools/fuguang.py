#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Daniel Yang on 2011-01-30.
Copyright (c) 2011 Yang. All rights reserved.
"""

import sys
import os
from twisted.internet import reactor, defer
from twisted.web.client import getPage, downloadPage

from BeautifulSoup import BeautifulSoup

from pymongo import Connection
import gridfs

connection = Connection()
db = connection.fuguang
table = db.cups

# page 1 - 46
BASE_URL = 'http://www.fuguangchina.com/product/list_3_%s.html'

data_list = []

def finish(r):
	print 'got', len(data_list)
	print 'inserting...'
	for data in data_list:
		table.insert(data)
	print 'done...'
	
	
def handleError(url, error):
	print 'got errpr', error
	
def processPage(pageContent, url):
	print url
	
	soup = BeautifulSoup(pageContent)
	spans = soup.findAll('span',{'class':'title04'})
	
	for span in spans:
		a = span.previousSibling.previousSibling
		name = span
		id = span.nextSibling.nextSibling
		
		data = {'link': a['href'], 'image':a.contents[0]['src'], 'name':name.text, 'serial':id.text}

		if data not in data_list:
				data_list.append(data)
dlist = []

for i in range(1, 48+1):
	url = BASE_URL % i
	pageFetchedDeferred = getPage(url)
	pageFetchedDeferred.addCallback(processPage, url)  
	pageFetchedDeferred.addErrback(handleError, url)
	dlist.append(pageFetchedDeferred)

dl = defer.DeferredList(dlist)
dl.addCallback(finish)

reactor.run()