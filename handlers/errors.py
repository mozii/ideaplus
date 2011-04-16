# encoding: utf-8
"""
errors.py

Created by Daniel Yang on 2011-02-24.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import cyclone
import cyclone.web

from utils.route_decorator import route
from handlers import BaseHandler


@route('/error/(\d+)/', name='error')
class ErrorHandler(BaseHandler):
    
    def get(self, code):
        template = "errors/%s.html" % code
        
        self.render(self.template_path+template)
        