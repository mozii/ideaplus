# encoding: utf-8
"""
main.py

Created by Daniel Yang on 2011-02-24.
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
from utils.url_shorten import encode_url, decode_url

from webhelpers.paginate import Page, PageURL

from handlers import BaseHandler

from db import *
from db.god import *

@route('/', name='main')
class MainHandler(BaseHandler):
    
    @defer.inlineCallbacks
    def get(self):
        
        page_num = self.get_argument('page', default=1, strip=True)
        try:
            page_num = int(page_num)
        except:
            page_num = 1
        
        invite_code = ''
        if self.current_user:
            invite_code = encode_url(self.current_user['num'], min_length=10)
        
        topic_count = yield topics_db.count()
        
        items_per_page = self.settings.front_topic_number
        url_for_page = PageURL(self.reverse_url('main'), {"page": "1"})
        page = Page(range(1, int(topic_count)+1), page=page_num, items_per_page=items_per_page ,url=url_for_page)
        
        f = txmongo.filter.sort(txmongo.filter.DESCENDING('last_repled_time'))

        topics = yield topics_db.find(filter=f, skip=((page_num-1)*items_per_page), limit=items_per_page)
        
        section_list = yield self.get_cache(cache_sections)
        if not section_list:
            section_list = yield get_sections()
            yield self.set_cache(cache_sections, section_list, 60)
        
        self.render(self.template_path+'index.html', 
            section_list=section_list, topics=topics, page=page, invite_code=invite_code)

@route('/m/(\w+)/', 'member')
class MemberHandler(BaseHandler):
    """成员个人信息页"""
    @defer.inlineCallbacks
    def get(self, member_account):
        member = yield members_db.find_one({'account':member_account})
        if not member:
            self.send_error(status_code=404)
        
        f = txmongo.filter.sort(txmongo.filter.DESCENDING('created'))
        
        topic_latest = yield topics_db.find({'member_id':str(member['_id'])}, filter=f, limit=10)
        
        key = (cache_pi % self.current_user['_id'])
        pi = yield self.get_cache(key)
        if not pi:
            pi = yield get_pi(self.current_user['account'])
            yield self.set_cache(key, pi, 10)
        
        following = False
        if self.current_user:
            following = yield follows_db.find_one({'follower': self.current_user['account'], 'followee': member['account']})
        
        reply_latest = yield replies_db.find({'member_id':str(member['_id'])}, filter=f, limit=10)
        
        self.render(self.template_path+'member.html', member=member,
                    topic_latest=topic_latest,
                    reply_latest=reply_latest,
                    following=following,
                    pi=pi)


@route('/signin/', name='signin')
class LoginHandler(BaseHandler):
    """登录"""
    def get(self):
        next = self.request.headers.get("Referer")
        if not next:
            next = self.get_argument('next', default='/')

        self.render(self.template_path+'login.html', next=next)
        
    
    @defer.inlineCallbacks
    def post(self):
        next = self.request.headers.get("Referer")
        if not next:
            next = self.get_argument('next', default='/')

        error_msgs = []
        
        remote_ip = self.request.remote_ip
        u = self.get_argument('u', default='', strip=True)
        p = self.get_argument('p', default='')
        
        hashed_password = hashlib.sha1(p).hexdigest()

        try:
            member = yield members_db.find_one({'account':u,'password':hashed_password},
                fields=['account', 'password', 'email', 'role', 'blocked',
                        'last_login', 'last_login_ip', 'num',
                        'invitor_name', 'invitor_email'])
            
            if member:
                if not member.get('blocked', False):
                    yield members_db.update({'account':member['account']}, {"$set": {"last_login":datetime.utcnow(), 'last_login_ip': self.request.remote_ip}})

                    member['_id'] = str(member['_id'])
                    member['password'] = 'oh~my~god~you~wont~get~it~here'
                    member['last_login'] = member['last_login'].strftime('%Y-%m-%d %H:%M:%S')
                    member['last_login_ip'] = self.request.remote_ip
                    self.set_secure_cookie("pinpin_user", cyclone.escape.json_encode(member))
                    
                    self.redirect(self.get_argument("next", default="/"))
                    return
                else:
                    error_msgs.append('帐号已经被停用,请反省...')
            else:
                error_msgs.append('帐号或者密码错误,请重新试试.')
                self.render(self.template_path+'login.html', error_msgs=error_msgs, account=u)
                
        except Exception as err:
            error_msgs.append('服务出现问题，请稍后再试.<br/> Message: %s' % err)
            self.render(self.template_path+'login.html', error_msgs=error_msgs)

@route('/signout/', name='signout')
class SignOutHandler(BaseHandler):
    """登出"""
    
    @cyclone.web.authenticated
    def get(self):
        self.clear_cookie("pinpin_user")
        self.redirect(self.get_argument("next", default="/"))

@route('/signup/', name='signup')
class JoinHandler(BaseHandler):
    """注册"""
    
    @defer.inlineCallbacks
    def get(self):
        next = self.request.headers.get("Referer")
        if not next:
            next = self.get_argument('next', default='/')
        
        next = self.get_argument('next', default='/')
        
        code = self.get_argument('c', default='')
        if not code:
            self.redirect(self.reverse_url('error', 4030))
            return
            
        member_num = decode_url(code)
        member = yield members_db.find_one({'num':member_num})
        if not member:
            self.send_error(status_code=404)
        
        captcha_html = captcha.displayhtml(self.settings.recaptcha_puk)
        
        self.render(self.template_path+'join.html', captcha_html=captcha_html, next=next)
    
    @defer.inlineCallbacks
    def post(self):
        next = self.request.headers.get("Referer")
        if not next:
            next = self.get_argument('next', default='/')

        code = self.get_argument('c', default='')
        if not code:
            self.redirect(self.reverse_url('error', 4030))
            return
            
        invitor_num = decode_url(code)
        invitor = yield members_db.find_one({'num':invitor_num})
        if not invitor:
            self.send_error(status_code=404)

        error_msgs = []
        
        remote_ip = self.request.remote_ip
        challenge = self.get_argument('recaptcha_challenge_field', default=None, strip=True)
        response  = self.get_argument('recaptcha_response_field', default=None, strip=True)
        cResponse = captcha.submit(challenge, response, self.settings.recaptcha_pvk, remote_ip)
        
        if not cResponse.is_valid:
            error_msgs.append('验证码错误,请再试试.')

        account = self.get_argument('account', default=None, strip=True)
        password = self.get_argument('password', default=None)
        email = self.get_argument('email', default=None, strip=True)
        
        import re
        p = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{5,20}$", re.IGNORECASE)
        if not (p.search(account)):
            error_msgs.append('帐号为5-20个英文字符')
            error_msgs.append('数字不能在最前')
        else:
            #check if this account exists.
            try:

                member = yield members_db.find_one({'account':account}, fields=['account'])

                if member:
                    error_msgs.append('这个帐号已经存在.如果您已经注册过但是忘记密码,您可以试试找回密码.')
            except Exception, e:
                error_msgs.append('服务出现错误,请稍后再试.')

        if not password or len(password)<6 or len(password)>32:
            error_msgs.append('密码为6-32个字符')
        
        if not email or len(email)>32:
            error_msgs.append('输入Email,不超过32个字符')
        else:
            p = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)
            if not (p.search(email)):
                error_msgs.append('Email格式不正确')
            
        
        #判断帐号是符合要求
        if error_msgs:
            captcha_html = captcha.displayhtml(self.settings.recaptcha_puk)
            self.render(self.template_path+'join.html', captcha_html=captcha_html,
                        error_msgs=error_msgs, account=account, email=email)
        else:
            #save
            num = yield members_db.count()
            
            hashed_password = hashlib.sha1(password).hexdigest()
            
            u = {
                        'account': account,
                        'password':hashed_password,
                        'email':email,
                        'created': datetime.utcnow(),
                        'num':num+1,
                        'updated': datetime.utcnow(),
                        'role': ['user'],
                        'last_login': datetime.utcnow(),
                        'last_login_ip': self.request.remote_ip,
                        'invitor_name': invitor['account'],
                        'invitor_email':invitor['email'],
                        }
            
            result = yield members_db.insert(u)
            
            member = u
            member['_id'] = str(u['_id'])
            member['password'] = 'oh~my~god~you~wont~get~it~here'
            member['last_login'] = u['last_login'].strftime('%Y-%m-%d %H:%M:%S')
            
            if result:
                self.set_secure_cookie("pinpin_user", cyclone.escape.json_encode(member))
                self.redirect(self.get_argument("next", default="/"))


@route('/n/(\w+)/', name='node')
class NodeHandler(BaseHandler):
    """版块页面"""
    
    @defer.inlineCallbacks
    def get(self, node_name):
        node = yield nodes_db.find_one({'name':node_name})
        
        if not node:
            self.send_error(status_code=404)
            
        user_role = self.current_user.get('role', [])
        if not 'root' in user_role:
            user_role = set(user_role)
            acl = set(node.get('acl', []))
            if not user_role.intersection(acl):
                self.redirect(self.reverse_url('error', 403))
        
        page_num = self.get_argument('page', default=1, strip=True)
        try:
            page_num = int(page_num)
        except:
            page_num = 1
        
        topic_count = node['topic_count']
        items_per_page = self.settings.topic_number
        url_for_page = PageURL(self.reverse_url('node', node['name']), {"page": "1"})
        page = Page(range(1, topic_count+1), page=page_num, items_per_page=items_per_page ,url=url_for_page)
        
        f = txmongo.filter.sort(txmongo.filter.DESCENDING('created'))
        
        topics = yield topics_db.find({'node_id':str(node['_id'])}, 
            filter=f, skip=((page_num-1)*items_per_page), limit=items_per_page)
        
        like_count = yield fav_db.count({'node_name': node['name']})
        
        has_fav = False
        if self.current_user:
            has_fav = yield fav_db.find_one({'node_name': node['name'], 'user_id':self.current_user['_id']})
        
        f_user = txmongo.filter.sort(txmongo.filter.DESCENDING('created'))
        
        fav_users = yield fav_db.find({'node_name': node['name']}, filter=f_user, limit=10)
        
        
        self.render(self.template_path+'node.html', 
            node=node, topics=topics, page=page, like_count=like_count, has_fav=has_fav, fav_users=fav_users,
        )


@route('/t/(\d*)/', name='topic')
class TopicHandler(BaseHandler):
    """话题页面"""
    
    
    @defer.inlineCallbacks
    def get(self, topic_num):
        try:
            topic_num = int(topic_num)
        except:
            topic_num = 1
        
        topic = yield topics_db.find_one({'num':topic_num})
        if not topic:
            self.send_error(status_code=404)
        
        page_num = self.get_argument('page', default=1, strip=True)
        try:
            page_num = int(page_num)
        except:
            page_num = 1

        #check sort.
        sort = self.get_argument('s', default='asc')
        
        url_params = {"page":1}
        
        if sort:
            url_params['s'] = sort
            if sort == 'des':
                f = txmongo.filter.sort(txmongo.filter.DESCENDING('num'))
            elif sort  == 'asc':
                f = txmongo.filter.sort(txmongo.filter.ASCENDING('num'))
        
        params = {'topic_num':topic['num']}
        
        #check show this users' only.
        show_user = self.get_argument('user', default='')
        if show_user:
            url_params['user'] = show_user
            
            params['member_name'] = topic['member_name']

        reply_count = topic.get('replies_num', 0)
        items_per_page = self.settings.reply_number
        url_for_page = PageURL(self.reverse_url('topic', topic['num']), url_params)
        page = Page(range(1, reply_count+1), page=page_num, items_per_page=items_per_page ,url=url_for_page)

        replies = yield replies_db.find(params, filter=f,
            skip=((page_num-1)*items_per_page), limit=items_per_page)
        
        like_count = yield fav_db.count({'topic_num':topic_num})
        
        has_fav = False
        if self.current_user:
            has_fav = yield fav_db.find_one({'topic_num':topic_num, 'user_id':self.current_user['_id']})
        
        #set view counter
        if self.current_user:
            #TODO set time delta.
            view = yield topic_views_db.find_one({'account':self.current_user['account'], 'topic_num':topic_num})
            if not view:
                r = yield topic_views_db.insert({'account':self.current_user['account'],
                                                'created': datetime.utcnow(),
                                                'topic_num':topic_num,
                                                })
                #update topic, too.
                view_num = topic.get('view_num', 0)
                topic['view_num'] = view_num + 1
                r = yield topics_db.save(topic)
        
        self.render(self.template_path+'topic.html', topic=topic, replies=replies, page=page, sort=sort, like_count=like_count, has_fav=has_fav)
    
    @defer.inlineCallbacks
    @cyclone.web.authenticated
    def post(self, topic_num):
        try:
            topic_num = int(topic_num)
        except:
            topic_num = 1
        
        topic = yield topics_db.find_one({'num':topic_num})
        
        if not topic:
            self.send_error(status_code=404)
        
        #TODO length.
        content = self.get_argument('content', default=None, strip=True)
        
        if not content:
            self.render(self.template_path+'topic.html', topic=topic, error_msgs=['请输入内容'])
        
        replies_num = topic.get('replies_num', 0)
        topic['replies_num'] = replies_num + 1
        topic['last_repled_id'] = self.current_user['_id']
        topic['last_repled_name'] = self.current_user['account']
        topic['last_repled_time'] = datetime.utcnow()
        
        r = topics_db.save(topic)
                
        reply = {
            'node_id': topic['node_id'],
            'node_name': topic['node_name'],
            'node_title':topic['node_title'],
            'topic_id': str(topic['_id']),
            'topic_num': topic['num'],
            'topic_title':topic['title'],
            'member_id': self.current_user['_id'],
            'member_name': self.current_user['account'],
            'member_email': self.current_user['email'],
            'content':content,
            'num': topic['replies_num'],
            'content_length': len(content),
            'created': datetime.utcnow(),
            'updated': datetime.utcnow(),
            'from_ip': self.request.remote_ip,
            'ua':self.request.headers.get("User-Agent"),
        }
        result = yield replies_db.insert(reply)
        
        self.redirect(self.reverse_url('topic', int(topic['num']))+('#r_%s' % topic['replies_num']))
        
        
@route('/n/(\w+)/new/', name='topic_new')
class CreateTopicHandler(BaseHandler):
    """创建话题页面"""
    
    
    @defer.inlineCallbacks
    @cyclone.web.authenticated
    def get(self, node_name):
        node = yield nodes_db.find_one({'name':node_name})
        if not node:
            self.send_error(status_code=404)
            
        self.render(self.template_path+'new_topic.html', node=node)

    @defer.inlineCallbacks
    @cyclone.web.authenticated
    def post(self, node_name):
        node = yield nodes_db.find_one({'name':node_name})
        
        if not node:
            self.send_error(status_code=404)
        
        error_msgs = []
        
        title = self.get_argument('title', default='', strip=True)
        content = self.get_argument('content', default='')
        if not title:
            error_msgs.append('请填入标题')
            self.render(self.template_path+'new_topic.html', node=node, error_msgs=error_msgs,
                title=title, content=content
            )
        #hoho
        if len(title)>120:
            if len(content)==0:
                content = title[120:]
            else:
                content = title[120:]+ ' : ' + content
                
            title = title[:119]
        
        topic_count = node.get('topic_count', 0)
        node['topic_count'] = topic_count + 1
        r = yield nodes_db.save(node)
        
        
        topic = {
            'node_id': str(node['_id']),
            'node_name': node['name'],
            'node_title':node['title'],
            'member_id': self.current_user['_id'],
            'member_name': self.current_user['account'],
            'member_email': self.current_user['email'],
            'title':title,
            'content':content,
            'num':node['topic_count'],
            'content_length': len(content),
            'created': datetime.utcnow(),
            'updated': datetime.utcnow(),
            'last_repled_time': datetime.utcnow(),
            'from_ip': self.request.remote_ip,
            'ua':self.request.headers.get("User-Agent"),
        }

        result = yield topics_db.insert(topic)
        
        self.redirect(self.reverse_url('topic', node['topic_count']))


