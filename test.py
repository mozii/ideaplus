#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
import txmongo
import cyclone.redis

from twisted.internet import defer, reactor
 
@defer.inlineCallbacks
def example():
    pass
    

if __name__ == '__main__':
    example().addCallback(lambda ign: reactor.stop())
    reactor.run()
