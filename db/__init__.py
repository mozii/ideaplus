# coding: utf-8
"""
__init__.py

difining databases

Created by Daniel Yang on 2011-02-22.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from settings import settings

#### databases
members_db = settings['mongo'].pinpin.members

fuguang_db = settings['mongo'].fuguang.fuguang
rate_db = settings['mongo'].pinpin.rates
comment_db = settings['mongo'].pinpin.comments
cache_db = settings['mongo'].pinpin.caches


sections_db = settings['mongo'].pinpin.sections
nodes_db = settings['mongo'].pinpin.nodes
topics_db = settings['mongo'].pinpin.topics
replies_db = settings['mongo'].pinpin.replies
topic_views_db = settings['mongo'].pinpin.topic_views
fav_db = settings['mongo'].pinpin.favs
follows_db = settings['mongo'].pinpin.follows



#### Const for cache keys.
cache_hot_nodes = 'fm.ide.cache.hot.notes'
cache_tags = 'fm.ide.cache.tags.%s'
cache_tag_could = 'fm.ide.cache.tag.cloud'
cache_sections = 'fm.ide.cache.sections'
cache_pi = 'fm.ide.cache.pi.%s'

cache_user_timeline = 'fm.ide.cache.tl.%s'
cache_user_notify = 'fm.ide.cache.notify.%s'
