import pandas as pd
fullPath = 'data/chengjiao-北京/2020-10-23-北京.xls'
fullPath = os.path.join(root, f)
#print(fullPath)
df = None
if f.endswith('.xls'):
    df = pd.read_excel(fullPath, converters = {'成交价(元/平)':lambda x:float(x),
                                                                    '链家编号':str, '产权年限':str})
elif f.endswith('.csv'):
    df = read_csv(fullPath, converters = {'成交价(元/平)':lambda x:float(x),
                                                                    '链家编号':str})
else:
    continue
if '单价（元/平米）' in df.columns:
    df['单价（元/平米）'] =  pd.to_numeric(df['单价（元/平米）'], errors="coerce")
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
except Exception as e:
    df.columns
    print('成交时间错误', e)
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
if len(df) > 0:
dfs.append(df)