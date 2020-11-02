# -*- coding: utf-8 -*-
from updatePlotUtil import *

import os
#计算城市排名
if not os.path.exists('fig/allcity'):
    os.makedirs('fig/allcity')
os.system('rm fig/allcity/*')
#cityList = ['北京', '上海','深圳']
#cityList = ['北京']
#cityList = ['深圳']
data = {}
res = {}
districtRes = {}
for city in cityList:
    print(city)
    df = read(city)
    data[city] = df
    res[city] = plotCity(df, city)
    districtRes[city] = plotAllDistrict(df, city)
for city in cityList:
    makeTable(districtRes[city], '城区', city)
makeTable(res)

    
