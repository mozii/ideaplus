#!/usr/bin/env python
# coding: utf-8
"""
run.py
Run twisted with autoload.

Created by Daniel Yang on 2011-02-24.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""


from twisted.scripts import twistd
from utils import autoreload

autoreload.main(twistd.run)