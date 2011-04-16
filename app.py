#!/usr/bin/env python
# coding: utf-8
"""
app.py

Created by Daniel Yang on 2011-02-22.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys, os

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


import cyclone
from twisted.python import log
from twisted.application import service, internet

#in case of using admin account, twistd can't find path.
sys.path.insert(0, '.')

#import this, or it will be 404.
from handlers import main, yipin, ajax, personal, errors

from utils.route_decorator import route
from settings import settings



webapp = cyclone.web.Application(route.get_routes(), **settings)

application = service.Application("pinpin.us")

pinpinService = internet.TCPServer(8080, webapp)
pinpinService.setServiceParent(application)
