# -*- coding: utf-8 -*-
from common import read, plot
import pandas as pd
import sys
import os

def plotArea(city, area, df = None):
    if df is None:
        df = read(city)
    df = df.dropna(subset = ['小区'])
    df = df.loc[df['小区'].str.contains(area)]
    if city == "北京":
        df = df.loc[df['成交价(元/平)']> 10000]
    print(city, area, 'data count:', len(df))
    if len(df) == 0:
        return df
    gp = df.groupby(['成交时间'])['成交价(元/平)']
    res=pd.DataFrame({"volume":gp.size(),"median_price":gp.median(), "mean_price":gp.mean()})
    res = res.iloc[:len(res),:]
    city = 'default'
    MA = True
    start_date = None
    force = True
    keep_all = True
    for ma_length in [1, 30, 60, 90]:
        title = '%s-%d日均线'%(area, ma_length)
        plot(res, city, title, MA, ma_length, start_date, force, keep_all)
    return df
def plotAreas(city, areas):
    dfs = []
    df = read(city)
    for area in areas:
        dfs.append(plotArea(city, area, df))
    df = pd.concat(dfs)
    print('data count:', len(df))
    gp = df.groupby(['成交时间'])['成交价(元/平)']
    res=pd.DataFrame({"volume":gp.size(),"median_price":gp.median(), "mean_price":gp.mean()})
    res = res.iloc[:len(res),:]
    city = 'default'
    MA = True
    start_date = None
    force = True
    keep_all = True
    for ma_length in [1, 30, 60, 90]:
        title = '%s-%d日均线'%('前滩', ma_length)
        plot(res, city, title, MA, ma_length, start_date, force, keep_all)
     
if __name__ == '__main__':
    if len(sys.argv) == 3:
        city = sys.argv[1]
        area = sys.argv[2]
        plotArea(city, area)
    elif len(sys.argv) == 2 and sys.argv[1] == "list":
        plotAreas('上海', ['晶耀名邸', '中粮前滩', '前滩三湘印象', '福晟钱隆', '浦江海德', '东方惠礼', '东方逸品', '江悦名庭', '东方悦耀'])
    else:
        print("usage: python3 plotAreaFromData.py [city] [area]")
