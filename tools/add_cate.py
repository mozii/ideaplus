# encoding: utf-8

import sys
import os
import re
if sys.getdefaultencoding() != 'utf-8':
        reload(sys)
        sys.setdefaultencoding('utf-8')


from pymongo import Connection


connection = Connection()
db = connection.fuguang
fuguang_table = db.fuguang



#db.fuguang.fuguang.find({url:/suliaobei/i}).skip(0).limit(30)
suliaobei = fuguang_table.find({'url': re.compile("suliaobei",re.IGNORECASE)})

for b in suliaobei:
        b['category'] = '塑料杯'
        fuguang_table.save(b)


baowenbei = fuguang_table.find({'url': re.compile("baowenbei",re.IGNORECASE)})

for b in baowenbei:
        b['category'] = '保温杯'
        fuguang_table.save(b)

bolibei = fuguang_table.find({'url': re.compile("bolibei",re.IGNORECASE)})

for b in bolibei:
        b['category'] = '玻璃杯'
        fuguang_table.save(b)

zishabei = fuguang_table.find({'url': re.compile("zishabei",re.IGNORECASE)})

for b in zishabei:
        b['category'] = '紫砂杯'
        fuguang_table.save(b)


paochashi = fuguang_table.find({'url': re.compile("paochashi",re.IGNORECASE)})

for b in paochashi:
        b['category'] = '泡茶师'
        fuguang_table.save(b)

yinbei = fuguang_table.find({'url': re.compile("yinbei",re.IGNORECASE)})

for b in yinbei:
        b['category'] = '银杯'
        fuguang_table.save(b)


fga = fuguang_table.find({'url': re.compile("fga",re.IGNORECASE)})

for b in fga:
        b['category'] = 'FGA'
        fuguang_table.save(b)

linpin = fuguang_table.find({'url': re.compile("lipin",re.IGNORECASE)})

for b in linpin:
        b['category'] = '礼品'
        fuguang_table.save(b)