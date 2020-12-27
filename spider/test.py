# -*- coding: utf-8 -*-
from chengJiaoSpider import chengJiaoInfo
spider = chengJiaoInfo('上海')
spider.generate_excle.addSheetExcle(u'在售列表')
re_get = 'https://sh.lianjia.com/chengjiao/107101494245.html'
spider.page = 1
spider.open_url(re_get,0)