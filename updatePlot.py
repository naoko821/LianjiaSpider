from common import read
from common import plot_df, plot_district, plot
import pandas as pd
def plotCity(df):
    gp = df.groupby(['成交时间'])['成交价(元/平)']
    res=pd.DataFrame({"volume":gp.size(),"median_price":gp.median(), "mean_price":gp.mean()})
    res = res.iloc[:len(res),:]
    title = city
    res = plot(res, city, title, MA, ma_length, start_date)
    return res
def plotAllDistrict(df):
    districts = list(df['下辖区'].unique())
    for district in districts:
        if str(district) != 'nan':
            plot_district(df, city, district, ma_length, start_date)
import os
MA = True
ma_length = 30
start_date = '2015-01-01'

cityList = ['北京', '上海', '深圳', '杭州', '广州', '长沙', '厦门', '宁波', '合肥', '成都','重庆','武汉',
            '西安','石家庄','苏州','南京', '大连', '青岛', '无锡', '保定', '温州', '廊坊']
#cityList = ['北京', '上海','深圳']
#cityList = ['宁波']
data = {}
res = {}
for city in cityList:
    print(city)
    df = read(city)
    data[city] = df
    res[city] = plotCity(df)
    plotAllDistrict(df)
#计算城市排名
if not os.path.exists('fig/allcity'):
    os.makedirs('fig/allcity')
os.system('rm fig/allcity/*')
median = {}
mean = {}
yearChange = {}
change = {}
monthChange = {}
for city in cityList:
    median[city] = int(res[city]['median_price'][-1])
    mean[city] = int(res[city]['mean_price'][-1])
    try:
        yearChange[city] = "%.2f%%"%(100 * (res[city]['median_price'][-1]/res[city]['median_price'][-365] - 1))
    except:
        yearChange[city] = '数据不足'
    change[city] = "%.2f%%"%(100 * (res[city]['median_price'][-1]/res[city]['median_price'][-180] - 1))
    monthChange[city] = "%.2f%%"%(100 * (res[city]['median_price'][-1]/res[city]['median_price'][-30] - 1))

cityRank = pd.DataFrame({'中位数':median, '均值':mean, 
                         '近一年':yearChange,
                         '近半年':change, '近一个月':monthChange}).sort_values('中位数', ascending = False)
cityRank['城市'] = cityRank.index
cityRank.index = range(1, len(cityRank) + 1)
cityRank = cityRank.loc[:,['城市', '中位数', '均值', '近一年', '近半年','近一个月']]
cityRank.to_excel("城市排名.xlsx")
for index, row in cityRank.iterrows():
    city = row['城市']
    index = int(index)
    cmd = 'cp fig/%s/%s.png fig/allcity/%.2d.%s.png'%(city, city, index, city)
    os.system(cmd)
