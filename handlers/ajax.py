# encoding: utf-8
"""
cache.py

Created by Daniel Yang on 2011-04-12.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys, os, hashlib

import cyclone, txmongo
import cyclone.web
from twisted.internet import defer


from handlers import BaseHandler

from utils.route_decorator import route

from db import *
from db.god import *

@route('/cache/follower', name='cache_follower')
class FollowerHandler(BaseHandler):
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self):
        f = txmongo.filter.sort(txmongo.filter.DESCENDING('created'))
        
        followers = yield follows_db.find({'follower': self.current_user['account']}, filter=f, limit=12)
        self.render(self.template_path+'partials/followers.html',   followers=followers)

@route('/cache/pi', name='cache_pi')
class PIHandler(BaseHandler):
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self):
        key = (cache_pi % self.current_user['_id'])
        
        pi = yield self.get_cache(key)
        if not pi:
            pi = yield get_pi(self.current_user['account'])
            yield self.set_cache(key, pi, 10)
            
        self.render(self.template_path+'partials/pi.html',   pi=pi)
                    
                    
@route('/cache/nodes', name='cache_hot_nodes')
class HotNodesHandler(BaseHandler):
    
    @defer.inlineCallbacks
    def get(self):
        
        hot_nodes = yield self.get_cache(cache_hot_nodes)
        if not hot_nodes:
            ##topic_count
            f = txmongo.filter.sort(txmongo.filter.DESCENDING('topic_count'))
            
            hot_nodes = yield nodes_db.find(filter=f, limit=10)
            
            yield self.set_cache(cache_hot_nodes, hot_nodes)
        
        self.render(self.template_path+'partials/hot_nodes.html', hot_nodes=hot_nodes)
        