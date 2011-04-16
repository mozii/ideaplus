# encoding: utf-8

import sys
import os
if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')

from pymongo import Connection
import gridfs
from twisted.internet import reactor, defer
from twisted.web import client
import ConfigParser

connection = Connection()
db = connection.fuguang
cup_table = db.cups

class HTTPProgressDownloader(client.HTTPDownloader):    
    def __init__(self, url, outfile, headers=None):
        client.HTTPDownloader.__init__(self, url, outfile, headers=headers)
        self.status = None

    def noPage(self, reason): # called for non-200 responses
        if self.status == '304':
            print reason.getErrorMessage()
            client.HTTPDownloader.page(self, '')
        else:
            client.HTTPDownloader.noPage(self, reason)

    def gotHeaders(self, headers):
        # page data is on the way
        if self.status == '200':
            
            # initialize for progress bar
            if headers.has_key('content-length'):
                self.totallength = int(headers['content-length'][0])
            else:
                self.totallength = 0
            self.currentlength = 0.0
            print ''

            # update headers metadata 
            oldheaders = {}
            eTag = headers.get('etag','')
            if eTag:
                oldheaders['etag'] = eTag[0]
            modified = headers.get('last-modified','')
            if modified:
                oldheaders['last-modified'] = modified[0]
                
            config = ConfigParser.ConfigParser()
            config.read('metadata.ini')
                
            if config.has_section('headers'):
                config.remove_section('headers')    
                
            config.add_section('headers')
            for key, value in oldheaders.items():
                config.set('headers', key, value)
                
            config.write(open('metadata.ini','w'))
            

        return client.HTTPDownloader.gotHeaders(self, headers)

    def pagePart(self, data):
        if self.status == '200':
            self.currentlength += len(data)
            if self.totallength:
                percent = "%i%%" % (
                    (self.currentlength/self.totallength)*100)
                
            else:
                percent = '%dK' % (self.currentLength/1000)
            print "\033[1FProgress: " + percent
        return client.HTTPDownloader.pagePart(self, data)

def downloadWithProgress(url, outputfile, contextFactory=None, *args, **kwargs):
    scheme, host, port, path = client._parse(url)
    factory = HTTPProgressDownloader(url, outputfile, *args, **kwargs)
    if scheme == 'https':
        from twisted.internet import ssl
        if contextFactory == None :
            contextFactory = ssl.ClientContextFactory()
        reactor.connectSSL(host, port, factory, contextFactory)
    else:
        reactor.connectTCP(host, port, factory)

    return factory.deferred



image_list = []
for page in cup_table.find():
	image_list.append(page['image'])

def downloadComplete(result):
    get_next_image()

def downloadError(err):
    print err

def get_next_image():
    if image_list and len(image_list) == 0:
        reactor.stop()
    print 'remain ', len(image_list), '----------------'
    
    url = str(image_list.pop())
    
    file_name = url.split('/')[-1]
    
    downloadWithProgress(url, file_name).addCallback(downloadComplete).addErrback(downloadError)

reactor.callLater(1, get_next_image)

reactor.run()





