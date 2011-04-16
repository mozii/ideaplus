#!/usr/bin/env python
# encoding: utf-8
"""
settings.py

Created by Daniel Yang on 2011-02-24.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys, os
#import txredisapi
import cyclone.redis
from utils.geoip import IPLocator

geoip_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "qqwry_11_4_5.dat"))
geoip = IPLocator(geoip_db)


from handlers.modules import *

settings = dict(
            app_name="pinpin",
            site_name="ide.fm",
            site_url = "http://localhost:8080",
            
            login_url="/signin",
            
            cookie_secret="X1AsPSKXRZO3hrSBYX2Abq4XFZpoIU/OnKP9wYQws7E=",
            recaptcha_pvk = "6Leuy8ESAAAAAA8DH1agK9O1aGTZbAiSV8AkM5ED",
            recaptcha_puk = "6Leuy8ESAAAAAC5kkdn25c53cQVG7eaGNMZ7Qa0s",
            
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            
            geoip = geoip,
            xsrf_cookies=True,
            mongo=txmongo.lazyMongoConnectionPool(),
            redis= cyclone.redis.lazyRedisConnectionPool(),
            
            front_topic_number = 10,
            topic_number = 20,
            reply_number = 5,
            product_number = 20,
            user_number = 15,
            
            invite_limit = 5,
            
            pager = '~2~ <span class="fade">(第 $page 页, 共 $page_count 页)</span>',
            ui_modules= {
                        "Topic": TopicModule,
                        "TimeSince": TimeSinceModule,
                        "HotNode": HotNodeModule,
                        "Reply": ReplyModule,
                        "Avatar":GravatarModule,
                        "Mention":MentionModule,
                        "Gist":GistModule,
                        "Escape":EscapeModule,
                        "Product":ProductModule,
                        "Comment": CommentModule,
                        "HotNode":HotNodeModule,
                        "Like": LikeModule,
                        "Follower": FollowerModule,
                         },
        )