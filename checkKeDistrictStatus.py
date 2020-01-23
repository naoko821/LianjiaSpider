 #-*- coding: utf-8 -*-
from pypinyin import lazy_pinyin
import os
dis = ['二七',
 '郑东新区',
 '荥阳市',
 '新郑市',
 '上街区',
 '巩义市',
 '新密市',
 '登封市',
 '中牟县',
 '经开区',
 '高新',
 '航空港区',
 '中原',
 '管城回族区',
 '惠济',
 '金水']
done = os.listdir('data/chengjiao-allzz/')
for d in dis:
 #   district = ''.join(lazy_pinyin(d.decode('utf8')))
    district = ''.join(lazy_pinyin(d))
    if district not in done:
        print(d)
