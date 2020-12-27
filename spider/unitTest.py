# -*- coding: utf-8 -*-
from chengJiaoSpider import chengJiaoInfo
area = '海淀'
url = 'https://bj.lianjia.com/chengjiao/pg{}rs%s/'%area
spider = chengJiaoInfo(area, url)
spider.start()
