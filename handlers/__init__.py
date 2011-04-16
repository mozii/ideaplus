# encoding: utf-8


import txmongo, re, cyclone, httplib
import cyclone.web

from twisted.internet import defer
import cPickle as pickle

class BaseHandler(cyclone.web.RequestHandler):
    """基本的Handler"""
    
    template_path = 'desktop/'
    
    def get_current_user(self):
        """获得当前用户"""
        
        user_json = self.get_secure_cookie("pinpin_user")
        if not user_json: return None
        return cyclone.escape.json_decode(user_json)
    
    def prepare(self):
        user_agent = self.request.headers.get("User-Agent")
        
        if (re.search('iPod|iPhone|Android|Opera Mini|BlackBerry|webOS|UCWEB|Blazer|PSP', user_agent)):
            template_path = 'mobile/'
    
    @defer.inlineCallbacks
    def delete_cache(self, key):
        """清除一个缓存,或者所有"""
        try:
            yield self.settings.redis.delete(key)
        except Exception, e:
            pass

    @defer.inlineCallbacks
    def get_cache(self, key):
        """获取缓存"""
        try:
            data = yield self.settings.redis.get(key)
            if not data:
                defer.returnValue(None)
            else:
                cached = pickle.loads(str(data))
                defer.returnValue(cached)
            
        except Exception, e:
            defer.returnValue(None)

    @defer.inlineCallbacks
    def set_cache(self, key, data, expire=600):
        """设置缓存, 默认10分钟"""
        try:
            if data:
                to_cache = pickle.dumps(data)
                r = yield self.settings.redis.set(key, to_cache)

                if expire>0:
                    yield self.settings.redis.expire(key, expire)
            
        except Exception, e:
            pass
