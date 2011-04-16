# encoding: utf-8
"""
personal.py

classes about personal services

Created by Daniel Yang on 2011-04-13.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys, os, hashlib

import cyclone, txmongo
import cyclone.web
from datetime import datetime

from twisted.python import log
from twisted.internet import defer

from recaptcha.client import captcha

from utils.route_decorator import route

from webhelpers.paginate import Page, PageURL

from handlers import BaseHandler

from db import *
from db.god import *



@route('/s/', 'setting')
class SettingHandler(BaseHandler):
    """个人设置页面"""
    
    @defer.inlineCallbacks
    @cyclone.web.authenticated
    def get(self):
        me = yield members_db.find_one({'account':self.current_user['account']})
        self.render(self.template_path+'setting.html', me=me)

    @defer.inlineCallbacks
    @cyclone.web.authenticated
    def post(self):
        error_msgs = []
        
        u = self.get_current_user()
        do = self.get_argument('do', default='')
        if do == 'profile':
            website = self.get_argument('website', default='')
            location = self.get_argument('location', default='')
            title = self.get_argument('title', default='')
            bio = self.get_argument('bio', default='')
            data = {
                    'website':website, 'location':location, 'title':title, 'bio':bio,
                }

            r = yield members_db.update({'account':u['account']}, {"$set": data})
            self.redirect(self.reverse_url('setting'))
            return
        elif do == 'password':
            password_current = self.get_argument('password_current', default='')
            password_new = self.get_argument('password_new', default='')
            if password_current and password_new:
                
                me = yield members_db.find_one({'account':u['account']},
                    fields=['account', 'password'])
                hashed = hashlib.sha1(password_current).hexdigest()
                hashed_new = hashlib.sha1(password_new).hexdigest()
                if hashed == me['password']:
                    r = yield members_db.update({'account':u['account']}, {"$set": {"password":hashed_new}})
                    self.redirect(self.reverse_url('setting'))
                    return
        
        self.redirect(self.reverse_url('setting'), error_msgs=error_msgs)
        
@route('/t/(\d*)/like/', name='topic_like')
class TopicLikeHandler(BaseHandler):
    """喜欢"""
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def post(self, topic_num):
        self.set_header("Content-Type", "text/plain")
        
        try:
            topic_num = int(topic_num)

            topic = yield topics_db.find_one({'num':topic_num})
            if not topic:
                self.send_error(status_code=404)
            
            has_fav = yield fav_db.find_one({'topic_num':topic_num, 'user_id':self.current_user['_id']})
    
            if not has_fav:
                    data = {
                        'type': 'topic',
                        'topic_num': topic['num'],
                        'topic_title':topic['title'],
                        'author_name': topic['member_name'],
                        'author_email': topic['member_email'],
                        'user_id':self.current_user['_id'],
                        'user_name': self.current_user['account'],
                        'user_email': self.current_user['email'],
                        'created': datetime.utcnow(),
                        }
                    r = yield fav_db.save(data)
            elif has_fav:
                    r = yield fav_db.remove({'topic_num':topic_num, 'user_id':self.current_user['_id']})
            self.finish("ok")
        except:
            self.finish("bad")


@route('/like/', name='like')
class LikeHandler(BaseHandler):

    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self):
        page_num = self.get_argument('page', default=1, strip=True)
        try:
            page_num = int(page_num)
        except:
            page_num = 1

        #check sort.
        f = txmongo.filter.sort(txmongo.filter.DESCENDING('created'))
        
        like_count = yield fav_db.count({'user_id':self.current_user['_id']})
        
        #let it be the same as topic_number
        items_per_page = self.settings.topic_number
        url_for_page = PageURL(self.reverse_url('like'), {"page": "1"})
        page = Page(range(1, int(like_count)+1), page=page_num, items_per_page=items_per_page ,url=url_for_page)
        
        
        likes = yield fav_db.find({'user_id':self.current_user['_id']}, filter=f,
            skip=((page_num-1)*items_per_page), limit=items_per_page)
        
        self.render(self.template_path+'like.html', likes=likes, page=page, like_count=like_count)



@route('/n/(\w*)/like/', name='node_like')
class NodeLikeHandler(BaseHandler):

    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def post(self, name):
        self.set_header("Content-Type", "text/plain")
        
        try:
            node = yield nodes_db.find_one({'name':name})
            if not node:
                self.send_error(status_code=404)
            
            has_fav = yield fav_db.find_one({'node_name':name, 'user_id':self.current_user['_id']})
    
            if not has_fav:
                    data = {
                        'type': 'node',
                        'node_name': node['name'],
                        'node_title':node['title'],
                        'user_id':self.current_user['_id'],
                        'user_name': self.current_user['account'],
                        'user_email': self.current_user['email'],
                        'created': datetime.utcnow(),
                        }
                    r = yield fav_db.save(data)
            elif has_fav:
                    r = yield fav_db.remove({'node_name':name, 'user_id':self.current_user['_id']})
                    
            self.finish("ok")
        except:
            self.finish("bad")


        
@route('/m/(\w*)/follow/', name='follow')
class FollowHandler(BaseHandler):
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self, account):
        page_num = self.get_argument('page', default=1, strip=True)
        #fi -> 我关注的, fd->我的粉丝
        follow_type = self.get_argument('ft', default='fi')
        
        try:
            page_num = int(page_num)
        except:
            page_num = 1
        
        member = yield members_db.find_one({'account':account})
        if not member:
            self.send_error(status_code=404)
        
        f = txmongo.filter.sort(txmongo.filter.DESCENDING('created'))
        
        following = (follow_type == 'fi')
        count = 0
        url_params = {"page":1}
        items_per_page = self.settings.user_number
        
        if follow_type == 'fi':
            count = yield follows_db.count({'follower': account})
            url_params['ft'] = 'fi'
            
            url_for_page = PageURL(self.reverse_url('follow', account), url_params)
            user_list = yield follows_db.find({'follower': account}, filter=f,
                skip=((page_num-1)*items_per_page), limit=items_per_page)
        elif follow_type =='fd':
            count = yield follows_db.count({'followee': account})
            url_params['ft'] = 'fd'
            
            url_for_page = PageURL(self.reverse_url('follow', account), url_params)
            user_list = yield follows_db.find({'followee': account}, filter=f,
                skip=((page_num-1)*items_per_page), limit=items_per_page)
        
        
        page = Page(range(1, int(count)+1), page=page_num, items_per_page=items_per_page ,url=url_for_page)
        self.render(self.template_path+'follow.html', following=following, page=page,
                    count=count, account=account, user_list=user_list)
    
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def post(self, name):
        self.set_header("Content-Type", "text/plain")
        try:
            member = yield members_db.find_one({'account':name})
            if not member:
                self.finish("bad")
            
            following = yield follows_db.find_one({'follower': self.current_user['account'], 'followee': name})
            
            if following:
                r = yield follows_db.remove({'follower': self.current_user['account'], 'followee': name})
            else:
                r = yield follows_db.save({'follower': self.current_user['account'],
                                           'followee': name,
                                           'followee-email': member['email'],
                                           'created': datetime.utcnow()})
            self.finish("ok")
            
        except Exception, e:
            self.finish("bad")
