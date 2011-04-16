#!/usr/bin/env python
# encoding: utf-8
"""
modules.py

Created by Daniel Yang on 2011-02-28.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import cyclone
import txmongo
from twisted.internet import defer

import hashlib

import datetime
import time
import re

class ProductModule(cyclone.web.UIModule):
    def render(self, product):
        return self.render_string("desktop/modules/product.html", product=product)

class CommentModule(cyclone.web.UIModule):
    def render(self, comment):
        return self.render_string("desktop/modules/comment.html", comment=comment)

class EscapeModule(cyclone.web.UIModule):
    def render(self, value):
        return value.replace("\n", "<br />")

# github gist script support
class GistModule(cyclone.web.UIModule):
    def render(self, value):
        return re.sub(r'(https://gist.github.com/[\d]+)', r'<script src="\1.js"></script>', value)


class MentionModule(cyclone.web.UIModule):
    def render(self, value):
        ms = re.findall('(@[a-zA-Z0-9\_]+\.?)\s?', value)
        if (len(ms) > 0):
            for m in ms:
                m_id = re.findall('@([a-zA-Z0-9\_]+\.?)', m)
                if (len(m_id) > 0):
                    if (m_id[0].endswith('.') != True):
                        value = value.replace('@' + m_id[0], '@<a href="/member/' + m_id[0] + '">' + m_id[0] + '</a>')
            return value
        else:
            return value


class YoukuModule(cyclone.web.UIModule):
    def render(self, value):
        videos = re.findall('(http://v.youku.com/v_show/id_[a-zA-Z0-9\=]+.html)\s?', value)

        if (len(videos) > 0):
            for video in videos:
                video_id = re.findall('http://v.youku.com/v_show/id_([a-zA-Z0-9\=]+).html', video)
                value = value.replace('http://v.youku.com/v_show/id_' + video_id[0] + '.html', '<embed src="http://player.youku.com/player.php/sid/' + video_id[0] + '/v.swf" quality="high" width="480" height="400" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash"></embed>')
            return value
        else:
            return value


# auto convert img.ly/abcd links to image tags
class ImglyModule(cyclone.web.UIModule):
    def render(self, value):
        imgs = re.findall('(http://img.ly/[a-zA-Z0-9]+)\s?', value)
        if (len(imgs) > 0):
            for img in imgs:
                img_id = re.findall('http://img.ly/([a-zA-Z0-9]+)', img)
                if (img_id[0] != 'system' and img_id[0] != 'api'):
                    value = value.replace('http://img.ly/' + img_id[0], '<a href="http://img.ly/' + img_id[0] + '" target="_blank"><img src="http://picky-staging.appspot.com/img.ly/show/large/' + img_id[0] + '" class="imgly" border="0" /></a>')
            return value
        else:
            return value

class LikeModule(cyclone.web.UIModule):
    def render(self, like):
        return self.render_string("desktop/modules/like.html", like=like)

class TopicModule(cyclone.web.UIModule):
    def render(self, topic, show_node=False):
        return self.render_string("desktop/modules/topic.html", topic=topic, show_node=show_node)


class ReplyModule(cyclone.web.UIModule):
    def render(self, reply):
        return self.render_string("desktop/modules/reply.html", reply=reply)


class GravatarModule(cyclone.web.UIModule):
    def render(self, email, size=40, image_type='jpg'):
        if email:
            email_hash = hashlib.md5(email).hexdigest()
            return "http://gravatar.com/avatar/{0}?s={1}.{2}?d=retro".format(email_hash, size, image_type)
        else:
            return 'http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm'

class HotNodeModule(cyclone.web.UIModule):
    def render(self):
        return self.render_string("desktop/right/right_hot.html")

class FollowerModule(cyclone.web.UIModule):
    def render(self):
        return self.render_string("desktop/right/right_follower.html")


def timesince(d, now=None):
    """
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
    then "0 minutes" is returned.

    Units used are years, months, weeks, days, hours, and minutes.
    Seconds and microseconds are ignored.  Up to two adjacent units will be
    displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
    possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.
    """
    chunks = (
      (60 * 60 * 24 * 365, '年'),
      (60 * 60 * 24 * 30, '月'),
      (60 * 60 * 24 * 7, '周'),
      (60 * 60 * 24, '天'),
      (60 * 60, '小时'),
      (60, '分钟')
    )
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.utcnow()

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return u'刚刚'
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    s = '%(number)d %(type)s' % {'number': count, 'type': name}
    if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            s += ', %(number)d %(type)s' % {'number': count2, 'type': name2}
    s+= '前'
    return s

def timeuntil(d, now=None):
    """
    Like timesince, but returns a string measuring the time until
    the given time.
    """
    if not now:
        now = datetime.datetime.utcnow()
    return timesince(now, d)


class TimeSinceModule(cyclone.web.UIModule):
    def render(self, d):
        return timesince(d)
