# encoding: utf-8
"""
auth.py

deal with google, facebook, twitter, weibo, 163....oauth...

Created by Daniel Yang on 2011-04-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import cyclone.web
import cyclone.auth
import cyclone.escape

from handlers import BaseHandler

from utils.route_decorator import route

from db import *
from db.god import *

@route('/auth/google/', name='google_auth')
class GoogleAuthHandler(BaseHandler, cyclone.auth.GoogleMixin):
    """
    Google will callback with data like:
    {'locale': u'en', 'first_name': u'Daniel', 'last_name': u'Yang', 'name': u'Daniel Yang', 'email': u'daniel.yang.zhenyu@gmail.com'}
    """
    
    
    @cyclone.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self._on_auth)
            return
        self.authenticate_redirect()


    def _on_auth(self, user):
        if not user:
            raise cyclone.web.HTTPError(500, "Google auth failed")
            
        ##save user to openid db.
        
        
        ##prepare new member object, and save it to db
        
        
        self.set_secure_cookie("user", cyclone.escape.json_encode(user))
        self.redirect(self.reverse_url('main'))