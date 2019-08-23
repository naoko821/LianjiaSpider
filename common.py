import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt
import matplotlib
from matplotlib import gridspec
from pypinyin import pinyin
import numpy as np
from matplotlib.font_manager import FontProperties
font=FontProperties(fname='font/Songti.ttc',size=18)

def read(city):
    dfs = []
    for root, dirs, files in os.walk('data/chengjiao-%s/'%city):
        #print(root, files, dirs)
        files.sort()
        for f in files:
            fullPath = os.path.join(root, f)
            print(fullPath)
            if f.endswith('.xls'):
                dfs.append(pd.read_excel(fullPath, converters = {'成交价(元/平)':lambda x:float(x),
                                                                              '链家编号':str}))
            if f.endswith('.csv'):
                dfs.append(pd.read_csv(fullPath, converters = {'成交价(元/平)':lambda x:float(x),
                                                                            '链家编号':str}))
    dfs0 = dfs
    dfs = []
    #统一格式
    for df in dfs0:
        df = df.rename(columns={'单价（元/平米）':'成交价(元/平)','所属小区':'小区','建筑面积：平米':'建筑面积',
                               '浏览(次)':'浏览（次）', '关注(人)':'关注（人）', '带看(次)':'带看（次）',
                               '所属下辖区':'下辖区', '房权所属':'产权所属', '房屋朝向':'朝向','调价（次）':'调价(次)',
                               '建成时间：年':'建成时间', '所属商圈':'商圈', '装修情况':'装修', '成交周期（天）':'成交周期(天)',
                               '房屋户型':'户型','产权年限':'土地年限', '楼层状态':'所在楼层', '挂牌价格（万）':'挂牌价格(万)',
                               '配备电梯':'电梯'})
        #去掉面积单位
        try:
            mj = df['建筑面积']
            mj_num = []
            for m in mj:
                m = str(m)
                if '㎡' in m:
                    m = m[:m.find('㎡')]
                try:
                    m = float(m)
                except:
                    m = np.nan
                mj_num.append(m)
            df['建筑面积'] = mj_num
        except:
            pass
        #统一成交时间格式
        try:
            time = []
            for t in df['成交时间']:
                t = str(t)
                if '/' in t:
                    t = '-'.join(t.split('/'))
                time.append(t)
            df['成交时间'] = time
        except:
            pass
        #去掉售价单位
        try:
            sj = df['售价(万)']
            sj_num = []
            for s in sj:
                s = str(s)
                if '万' in s:
                    s = s[:s.find('万')]
                if '-' in s:
                    #print(s)
                    s = s.split('-')[-1]
                s = float(s)
                sj_num.append(s)
            df['售价(万)'] = sj_num
        except:
            pass
        try:
            df['成交价(元/平)'] = pd.to_numeric(df['成交价(元/平)'], errors='coerse')
        except:
            pass
        dfs.append(df)

    df = pd.concat(dfs)
    df = df.drop_duplicates(subset=['链家编号'])
    df = df.loc[df['成交价(元/平)']> 1000]
    print(len(df))
    return df


MA = True
#MA = False
ma_length = 30
start_date = '2017-01-01'
city = 'default'
def get_moving_average(res, ma_length):
    volume_ma = []
    median_ma = []
    mean_ma = []
    for i in range(len(res) - ma_length):
        volume_ele = sum(res['volume'].iloc[i:i+ma_length])
        median_ele = 0
        mean_ele = 0
        for j in range(i, i + ma_length):
            median_ele += res['volume'].iloc[j] * res['median_price'].iloc[j]
            mean_ele += res['volume'].iloc[j] * res['mean_price'].iloc[j]
        volume_ma.append(volume_ele)    
        median_ma.append(median_ele/volume_ele)
        mean_ma.append(mean_ele/volume_ele)
    return pd.DataFrame({'volume':volume_ma, 'median_price':median_ma,  'mean_price':mean_ma}, 
                        index = res.index[ma_length:])

def plot(res, city, title, MA, ma_length, start_date = None):
    if  len(res)< 10 + ma_length:
        return
    if MA == True:
        res = get_moving_average(res, ma_length)
    if start_date is not None:
        res = res.loc[res.index > start_date,:]
    plt.rcParams['font.sans-serif']=['SimHei']
    matplotlib.rc('font', size=18)
    matplotlib.rcParams['figure.figsize'] = [15, 10]
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
    ax0 = plt.subplot(gs[0])
    ax0.plot(res['median_price'])
    ax0.plot(res['mean_price'])
    ax0.legend(['median price','mean price'])
    plt.setp( ax0.get_xticklabels(), visible=False)
    plt.title(title, fontproperties = font)
    xticks = ax0.xaxis.get_major_ticks()
    interval = len(xticks)// 10
    ax0.set_xticks(ax0.get_xticks()[::interval])
    plt.grid(True)
    ax1 = plt.subplot(gs[1])
    ax1.bar(res.index, res['volume'])
    xticks = ax1.xaxis.get_major_ticks()
    interval = len(xticks)// 10
    xticks = ax1.get_xticks()
    target_xticks = xticks[::interval]
    target_xticks = target_xticks[:-1] + [xticks[-1]]
    ax1.set_xticks(target_xticks)
    plt.xticks(rotation=30)
    dir_name = os.path.join('fig', city)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    plt.savefig(os.path.join(dir_name, title +'.png'))
    plt.show()
    plt.close()

def plot_district(df, city, district ='朝阳', ma_length = -1, start_date = None):
    gp = df.loc[df['下辖区']==district].groupby(['成交时间'])
    res = pd.DataFrame({'volume':gp.size(),'mean_price':gp['成交价(元/平)'].mean(),
                        'median_price':gp['成交价(元/平)'].median()})
    res = res.iloc[:len(res) -1,:]
    print(district)
    title = district
    plot(res, city, title, MA, ma_length, start_date)
def plot_df(df, city, title, MA, ma_length):  
    gp = df.groupby(['成交时间'])['成交价(元/平)']
    res=pd.DataFrame({"volume":gp.size(),"median_price":gp.median(), "mean_price":gp.mean()})
    res = res.iloc[:len(res)-1,:]
    plot(res, city, title, MA, ma_length)
    
def plot_dfs(dfs, title, legends, ma_length = 30, start_date = None):
    ress = []
    for df in dfs:
        gp = df.groupby(['成交时间'])['成交价(元/平)']
        res=pd.DataFrame({"volume":gp.size(),"median_price":gp.median(), "mean_price":gp.mean()})
        res = res.iloc[:len(res)-1,:]
        if  len(res)< 10 + ma_length:
            return
        if ma_length != -1:
            res = get_moving_average(res, ma_length)
        if start_date is not None:
            res = res.loc[res.index > start_date,:]
        ress.append(res)
    
    plt.rcParams['font.sans-serif']=['SimHei']
    matplotlib.rc('font', size=18)
    matplotlib.rcParams['figure.figsize'] = [15, 10]
    index = ress[0].index
    for res in ress:
        res = res.loc[res.index.isin(index)]
        plt.plot(res['mean_price']/res['mean_price'].iloc[0])
    plt.legend(legends, prop = font)
    plt.title(title, fontproperties = font)
    ax0 = plt.gca()
    xticks = ax0.xaxis.get_major_ticks()
    interval = len(xticks)// 10
    ax0.set_xticks(ax0.get_xticks()[::interval])
    plt.xticks(rotation=30)
    plt.grid(True)
    dir_name = os.path.join('fig', city)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    plt.savefig(os.path.join(dir_name, title +'.png'))
    plt.show()
    plt.close()