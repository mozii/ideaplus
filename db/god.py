# coding: utf-8
"""
db.py

map/reduce to cache.


Created by Daniel Yang on 2011-04-12.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import re
from txmongo.dbref import DBRef
from twisted.internet import defer
from db import *

@defer.inlineCallbacks
def process_mention(content):
    ms = re.findall('(@[a-zA-Z0-9\_]+\.?)\s?', content)
    if (len(ms) > 0):
            for m in ms:
                m_id = re.findall('@([a-zA-Z0-9\_]+\.?)', m)
                if (len(m_id) > 0):
                    if (m_id[0].endswith('.') != True):
                        pass
                    
    

@defer.inlineCallbacks
def get_pi(account):

    pi = {}
    fav_count = yield fav_db.count({'user_name':account})
    pi['fav_count'] = fav_count
    
    following_count = yield follows_db.count({'follower': account})
    followed_count = yield follows_db.count({'followee': account})
    pi['following_count'] = following_count
    pi['followed_count'] = followed_count
    
    defer.returnValue(pi)


@defer.inlineCallbacks
def get_product_rates(pid):
    """获得一个产品的评分和tag"""
    result = yield rate_db.map_reduce(
            map = "function(){emit(this.product_id, {'rate': this.rate, 'count':1, tags: this.tags});}",
            reduce = """
                function(key, values) {
                        var result = {'rate': 0, 'count':0, tags: []}
                        
                        values.forEach(function(value){
                                result.rate += value.rate;
                                result.count += value.count;
                                
                                value.tags.forEach(function(tag){
                                        result.tags.push(tag);
                                });
                                
                        });
                        return result;
                }
            """,
            finalize = """
                function Finalize(key, reduced){
                    result = { 'avg':reduced.rate/reduced.count, 'tags': reduced.tags, 'rate_count': reduced.count }
                    return result;
                }
            """,
        full_response = True,
        query = {'product_id': pid},
        out = {'inline':1},
        )
    defer.returnValue(result)


@defer.inlineCallbacks
def get_tag_cloud():
    result = yield rate_db.map_reduce(
        map = "function(){ this.tags.forEach(function(tag){  emit(tag, 1)  }); }",
        reduce = """
            function(key, values) {
                var count = 0;
                values.forEach(function(v){
                    count += v;
                });
                return count; 
            }
        """,
        full_response = True,
        out = {'inline':1},
    )
    
    defer.returnValue(result)


@defer.inlineCallbacks
def get_sections():
    #获取按照section分的所有话题组
    result = yield nodes_db.group(
        keys=['section'],
        initial={'nodes':[]},
        reduce = "function(obj, prev) { prev.nodes.push(obj) }",
    )
    
    section_list = []
    for s in result['retval']:
        if isinstance(s["section"], DBRef):
            ref = s["section"]

            section = yield sections_db.find_one(ref.id)
            
            section_list.append(
                {'section': section, 'nodes':s['nodes']}
            )
    defer.returnValue(section_list)





