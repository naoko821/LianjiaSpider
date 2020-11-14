from common import read
from common import plot_df, plot_district, plot
from common import updateCityTable, render_mpl_table
import pandas as pd
import numpy as np
from spider.setting import cityList
from weasyprint import HTML
import os

MA = True
ma_length = 30
start_date = '2015-01-01'

def plotCity(df, city):
    if city == '苏州':
        df_select = df.loc[df['下辖区'].isin(set(['吴中', '姑苏', '工业园区','高新']))]
        gp = df_select.groupby(['成交时间'])['成交价(元/平)']
    if city == '天津':
        df_select = df.loc[df['下辖区'].isin(set(['和平', '北辰', '东丽', '红桥', '河北', '西青', '河东', '河西', '南开']))]
        gp = df_select.groupby(['成交时间'])['成交价(元/平)']
    else:
        gp = df.groupby(['成交时间'])['成交价(元/平)']
    res=pd.DataFrame({"volume":gp.size(),"median_price":gp.median(), "mean_price":gp.mean()})
    res = res.iloc[:len(res),:]
    title = city
    res = plot(res, city, title, MA, ma_length, start_date, False, True)
    return res
def plotAllDistrict(df, city):
    districts = list(df['下辖区'].unique())
    res = {}
    for district in districts:
        if str(district) != 'nan':
            res[district] = plot_district(df, city, district, ma_length, start_date)
    return res

def makeTable(res, cityLevel='城市', cityName = None):
    print('compute change of', cityName)
    median = {}
    mean = {}
    yearChange = {}
    change = {}
    monthChange = {}
    drawDown = {}
    updateTime = {}
    for city in res.keys():
        print("compute", city, "of", cityName)
        if res[city] is None or len(res[city]) < 30:
            continue
        median[city] = int(res[city]['median_price'][-1])
        mean[city] = int(res[city]['mean_price'][-1])
        updateTime[city] = res[city].index[-1]
        try:
            yearChange[city] = "%.2f%%"%(100 * (res[city]['median_price'][-1]/res[city]['median_price'][-365] - 1))
        except:
            yearChange[city] = '数据不足'
        try:
            change[city] = "%.2f%%"%(100 * (res[city]['median_price'][-1]/res[city]['median_price'][-180] - 1))
        except:
            change[city] = '数据不足'
        try:
            monthChange[city] = "%.2f%%"%(100 * (res[city]['median_price'][-1]/res[city]['median_price'][-30] - 1))
        except:
            monthChange[city] = '数据不足'
        df = res[city]
        df = df.loc[df['volume'] > df['volume'].mean() * 0.5, :]
        drawDown[city] = "%.2f%%"%(100 * (df['median_price'][-1]/np.nanmax(df['median_price'])- 1))
    cityRank = pd.DataFrame({'中位数':median, '均值':mean, 
                         '近一年':yearChange,
                         '近半年':change, '近一个月':monthChange, '前高以来':drawDown,
                         '最新数据日期':updateTime}).sort_values('中位数', ascending = False)
    cityRank[cityLevel] = cityRank.index
    cityRank.index = range(1, len(cityRank) + 1)
    cityRank = cityRank.loc[:,[cityLevel, '中位数', '均值', '近一年', '近半年','近一个月', '前高以来', '最新数据日期']]
    if not os.path.exists('rank'):
        os.makedirs('rank')
    if cityName == None:
        filename = 'rank/城市排名.xlsx'
        imgfilename = 'fig/allcity/table.png'
        for index, row in cityRank.iterrows():
            city = row[cityLevel]
            index = int(index)
            cmd = 'cp fig/%s/%s.png fig/allcity/%.2d.%s.png'%(city, city, index, city)
            os.system(cmd)
    else:
        filename = 'rank/%s区域排名.xlsx'%cityName
        imgfilename = 'fig/%s/table.png'%cityName
    cityRank.to_excel(filename)
    render_mpl_table(cityRank, imgfilename, header_columns=0, col_width=2.0) 

