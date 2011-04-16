#!/usr/bin/env python
# encoding: utf-8
"""
yipin.py

Created by Daniel Yang on 2011-03-5.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys, os, re, hashlib

import txmongo
import cyclone.web
from datetime import datetime

from twisted.python import log
from twisted.internet import defer

from db import *
from db.god import *

from utils.route_decorator import route
from webhelpers.paginate import Page, PageURL

from handlers import BaseHandler

from utils import countDuplicatesInList


@route('/prd/', name='fg')
class ProductsHandler(BaseHandler):

    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self):
        page_num = self.get_argument('page', default=1, strip=True)
        try:
            page_num = int(page_num)
        except:
            page_num = 1

        param = {}

        url_param = {"page": "1"}
        category = self.get_argument('category', default='')
        
        count = yield fuguang_db.count()
        
        if category:
            #param['url'] = re.compile(category,re.IGNORECASE)
            param['category'] = category
            url_param['category'] = category.encode("utf8")
            count = yield fuguang_db.count(param)
        
        items_per_page = self.settings.product_number

        url_for_page = PageURL(self.reverse_url('fg'), url_param)
        page = Page(range(1, int(count)+1), page=page_num, items_per_page=items_per_page ,url=url_for_page)
        
        f = txmongo.filter.sort(txmongo.filter.ASCENDING('number'))
        
        products = yield fuguang_db.find(param, filter=f, skip=((page_num-1)*items_per_page), limit=items_per_page)
        
        #tag cloud.
        
        tag_could = yield self.get_cache(cache_tag_could)
        if not tag_could:

            result = yield get_tag_cloud()
            
            if result['ok'] and result.get('results'):
                tag_could = result.get('results')
                yield self.set_cache(cache_tag_could, tag_could)
            else:
                tag_could = []
        
        self.render(self.template_path+'products.html', page=page, products=products, tag_could=tag_could, category=category)


@route('/prd/dummy/', name='dummy')
class DummyHandler(BaseHandler):
    def get(self):
        self.render('dummy.data')



@route('/prd/v/(\d*)/', name='product')
class ProductHandler(BaseHandler):
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self, prod_num):
        try:
            prod_num = int(prod_num)
        except:
            page_num = 0

        product = yield fuguang_db.find_one({'number': prod_num})
        
        if not product:
            self.send_error(status_code=404)


        key = (cache_tags % prod_num)
        rate_data = yield self.get_cache(key)

        if not rate_data:
            result = yield get_product_rates(str(product['_id']))

            if result['ok'] and result.get('results'):
                rate_data = result['results'][0]['value']
                rate_data['tags'] = countDuplicatesInList(rate_data['tags'])
                
                yield self.set_cache(key, rate_data)
            else:
                rate_data = []

        rate = yield rate_db.find_one({ 'product_id' : str(product['_id']), 'member_id': self.current_user['_id'] })
        has_rated = (rate != {})
        
        f = txmongo.filter.sort(txmongo.filter.DESCENDING('created'))
        comments = yield comment_db.find({ 'product_id' : str(product['_id'])}, filter=f)
        has_comment = ( comments != [] )
        
        
        self.render(self.template_path+'product.html', product=product, rate=rate, comments=comments,
                    has_rated=has_rated, has_comment=has_comment, rate_data=rate_data)
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def post(self, prod_num):
        k = self.get_argument('k', default='')
        rate = self.get_argument('star2', '3')
        tags = self.request.arguments.get('select3[]', [])
        
        try:
            prod_num = int(prod_num)
            rate = int(rate)
        except:
            page_num = 0
            rate = 3

        product = yield fuguang_db.find_one({'number': prod_num})
        
        if not product:
            self.send_error(status_code=404)
        
        error_msgs = []

        if k == 'ratentag':
            #check if I have commented:
            comment = yield rate_db.find_one({ 'product_id' : str(product['_id']), 'member_id': self.current_user['_id'] })
            if comment:
                comment['rate'] = rate
                comment['tags'] = tags
                comment['updated'] = datetime.utcnow()
                comment['from_ip'] = self.request.remote_ip
                
                result = yield rate_db.save(comment)
            else:
                data = {
                    'product_id' : str(product['_id']),
                    'product_name': product['name'],
                    'product_number': product['number'],
                    'member_id': self.current_user['_id'],
                    'member_name': self.current_user['account'],
                    'rate' : rate,
                    'tags' : tags,
                    'created': datetime.utcnow(),
                    'updated': datetime.utcnow(),
                    'from_ip': self.request.remote_ip,
                }
                
                #save first.
                result = yield rate_db.insert(data)
            
        
        if k == 'comment':
            comment = self.get_argument('comment', default='')
            if comment:
                data = {
                'product_id' : str(product['_id']),
                'product_name': product['name'],
                'member_email': self.current_user['email'],
                'member_id': self.current_user['_id'],
                'member_name': self.current_user['account'],
                'comment': comment,
                'created': datetime.utcnow(),
                'updated': datetime.utcnow(),
                'from_ip': self.request.remote_ip,
                }
                result = yield comment_db.insert(data)
                
            else:
                error_msgs.append('请填入标题')
           
        
        self.redirect(self.reverse_url('product', prod_num))


@route('/prd/tag/(\w*)/', name='tag')
class TagHandler(BaseHandler):
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self, tag):
        pass
