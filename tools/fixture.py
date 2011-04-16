#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
import txmongo
from txmongo.dbref import DBRef

from twisted.internet import defer, reactor
 
@defer.inlineCallbacks
def example():
    mongo = yield txmongo.MongoConnection()

    db = mongo.pinpin  #  database
    members = db.members  # collection
    sections = db.sections
    nodes = db.nodes
    topics_db = db.topics
    replies = db.replies

    daniel = {
                         'account': 'daniel',
                         'password':'7ce659a787c2a00bea4aae49e939b2d43fd12428',
                         'email':'daniel.yang.zhenyu@gmail.com',
                         'role': ['root'],
                        'title': '资深代码工',
                         'created': datetime.now(),
                         'updated': datetime.now(),
                         'last_login': datetime.now(),
                         'last_login_ip':'127.0.0.1',
                         'website': 'http://pinpin.us',
                         'location':'',
                         'bio':'',
                         'twitter':'',
                         'location':'',
                         'avatar':'',
                         'num': 1,
                         'blocked': False,
                         }
    table = {
                         'account': 'table',
                         'password':'7ce659a787c2a00bea4aae49e939b2d43fd12428',
                         'email':'tablef@gmail.com',
                         'title': '资深SP大忽悠',
                         'role': ['root'],
                        'num': 2,
                         'created': datetime.now(),
                         'updated': datetime.now(),
                         'last_login': datetime.now(),
                         'last_login_ip':'127.0.0.1',
                         }
    robot = {
                         'account': 'robot',
                         'password':'7ce659a787c2a00bea4aae49e939b2d43fd12428',
                         'email':'test@gmail.com',
                         'title': '我是机器人',
                         'created': datetime.now(),
                         'updated': datetime.now(),
                         'last_login': datetime.now(),
                         'last_login_ip':'127.0.0.1',
                         'num':3,
                         'role': ['user'],
                         }
     
     
    r = yield members.insert([daniel, table, robot], True)
    
    sectiion_1 = {
                     'name':'Internet',
                     'title':'互联网',
                     'order': 0,
                     'created': datetime.now(),
                     'updated': datetime.now(),
     }
    
    sectiion_2 = {
                      'name':'Share',
                      'title':'分享发现',
                      'order': 1,
                      'created': datetime.now(),
                      'updated': datetime.now(),
      }
    
    sectiion_3 = {
                      'name':'inter',
                      'title':'内部',
                      'order': 2,
                      'created': datetime.now(),
                      'updated': datetime.now(),
      }
     
    s_1 = yield sections.insert(sectiion_1, True)
    s_2 = yield sections.insert(sectiion_2, True)
    s_3 = yield sections.insert(sectiion_3, True)
    
    node_1 = {
                     'name':'yipin',
                     'title':'富光壹品',
                     'theme':'default',
                     'order': 0,
                     'desc':'富光壹品官方',
                     'acl':['user'],
                     'topic_count':0,
                     'icon': 'default.gif',
                     'created': datetime.now(),
                     'updated': datetime.now(),
                     'section':DBRef(sections, s_1)
     }
     
     
    node_2 = {
                     'name':'qa',
                     'title':'问与答',
                     'desc':'问与答',
                     'acl':['user'],
                     'theme':'default',
                     'order': 0,
                     'icon': 'default.gif',
                     'topic_count':0,
                     'created': datetime.now(),
                     'updated': datetime.now(),
                     'section':DBRef(sections, s_2)
     }
     
    node_3 = {
                      'name':'share',
                      'title':'这货是啥',
                      'desc':'分享我的新发现',
                      'acl':['user'],
                      'theme':'default',
                      'order': 1,
                      'icon': 'default.gif',
                      'topic_count':0,
                      'created': datetime.now(),
                      'updated': datetime.now(),
                      'section':DBRef(sections, s_2)
      }
    
    node_4 = {
                      'name':'ig',
                      'title':'一般讨论',
                      'desc':'一般讨论',
                      'acl':['root'],
                      'theme':'default',
                      'order': 1,
                      'icon': 'default.gif',
                      'topic_count':0,
                      'created': datetime.now(),
                      'updated': datetime.now(),
                      'section':DBRef(sections, s_3)
      }
     
     
    n_r = yield nodes.insert([node_1, node_2, node_3, node_4], True)
     
    print 'done......'
     
    

if __name__ == '__main__':
    example().addCallback(lambda ign: reactor.stop())
    reactor.run()
