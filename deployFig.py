# -*- coding: utf-8 -*-
import os
import pandas as pd

img_html_tmp = '<img alt="{city}" src="http://www.yeshiwei.com/fig/{dirname}">'
wxml_tmp = '''<!--pages/fangjia/fangjia.wxml-->
<view class="container">
<ad unit-id="adunit-35015dc194c26a95"></ad>
    <view>
  <official-account></official-account>
  </view>
  <!-- 导航 -->
  <view class="list">

    <view class="list-item">
      <text class="request-text">房价走势</text>
    </view>
    
    {buttons}
  </view>
  <view>

  {citydata}

    <div class="nav">
      <button class="next" size="mini" type="default" bindtap="goHome">回到首页</button>
    </div>
  </view>
</view>
'''
img_wxml_tmp = ''' <view wx:if="{{{{city === '{city}' && district === '{district}'}}}}">
 <image class="image3" src="cloud://shiwei-mwhas.7368-shiwei-mwhas-1301568844/{city}-**-{filename}" mode="scaleToFill"></image>
 </view>
 '''
button_line_tmp = '''
    <view class="list-item">
{buttons}
    </view>
'''
button_wxml_tmp = '''
    <div class="nav">
      <button class="next" size="mini" type="default" data-city = '{city}' bindtap="gotoCity">{citydes}</button>
    </div>
    '''
district_button_wxml_tmp = '''
    <div class="nav">
      <button class="next" size="mini" type="default" data-city = '{city}' data-district='{district}' bindtap="gotoDistrict">{district}</button>
    </div>
    '''

wxml_city_tmp = '''
  <!-- {citydes} -->
  <view class="guide" wx:if="{{{{city === '{city}'}}}}">
    <text class="headline">{citydes}</text>
    {img}
    <view class="list">
    {city_button}
    </view>
  </view>
'''


rootDir = 'fig/'
dirNames = os.listdir(rootDir)


citydesMap = {'allcity':'全部城市','default':'草稿'
}

head_template = '''		                    <div class="table-head">
{content}
		                    </div>'''
row_template = '''		                    <div class="table-row">
{content}
		                    </div>'''
element_temp = '''		                        <div class="serial">{value}</div>
'''
image_template = '''		                <div class="col-md-4">
		                    <a href="{url}" class="img-pop-up">
		                        <div class="single-gallery-image" style="background: url({url});"></div>
		                    </a>
		                </div>'''
dirName = 'fig/'
def getCityHTML(city):
    df = pd.DataFrame()
    if city not in ['房价收入分析']:
        if city == 'allcity':
            df = pd.read_excel('rank/城市排名.xlsx')
        else:
            df = pd.read_excel('rank/%s区域排名.xlsx'%city)
        table_html = ""
        content = element_temp.format(value='#')
        for col in df.columns:
            content += element_temp.format(value=col)
        table_html += head_template.format(content=content)
        for index, row in df.iterrows():
            content = element_temp.format(value=str(index))
            for col in df.columns:
                content += element_temp.format(value = str(row[col]))
            table_html += row_template.format(content = content)
    else:
        table_html = ""
    image_html = ""
    districts = os.listdir(os.path.join(dirName, city))
    districts_sorted = []
    if '城区' in df.columns or '城市' in df.columns:
        for d in districts:
            if city in d:
                districts_sorted.append(d)
        s = pd.Series()
        if '城区' in df.columns:
            s = df['城区']
        else:
            s = df['城市']
        for district in s:
            for d in districts:
                if district in d and district not in districts_sorted:
                    districts_sorted.append(d)
        for d in districts:
            if not d in districts_sorted:
                districts_sorted.append(d)
        districts = districts_sorted
    for district in districts:
        if not district.endswith('.png'):
            continue
        url = 'http://www.yeshiwei.com/fig/{city}/{district}'.format(city = city, district = district)
        image_html += image_template.format(url=url)
    html = open('fangjia_template.html').read().format(city = city, table = table_html, image = image_html)
    fp = open('fangjia/%s.html'%city,'w')
    fp.write(html)
    fp.close()

def makeWeixin(city):
    df = pd.DataFrame()
    if city not in ['房价收入分析']:
        if city == 'allcity':
            df = pd.read_excel('rank/城市排名.xlsx')
        else:
            df = pd.read_excel('rank/%s区域排名.xlsx'%city)
    dirName = os.path.join(rootDir, city)
    files = os.listdir(dirName)
    files.sort(reverse=False)
    img_wxml = ""
    button_wxml = ""
    for f in files:
        if city in f:
            files.remove(f)
            files = [f, *files]
            break
    button_buf = ''
    current_line_char_num = 0
    districts_sorted = []
    if '城区' in df.columns or '城市' in df.columns:
        for d in files:
            if city in d:
                districts_sorted.append(d)
        s = pd.Series()
        if '城区' in df.columns:
            s = df['城区']
        else:
            s = df['城市']
        for district in s:
            for d in files:
                if district in d and district not in districts_sorted:
                    districts_sorted.append(d)
        for d in files:
            if not d in districts_sorted:
                districts_sorted.append(d)
        files = districts_sorted
    for f in files:
        if not f.endswith('.png'):
            continue
        district = f.split(".")[0]
        img_wxml_ele = img_wxml_tmp.format(city = city, district = district, filename = f) 
        img_wxml += img_wxml_ele
        button_wxml_ele = district_button_wxml_tmp.format(city = city, district = district)
        if current_line_char_num + len(district) > 10:
            button_wxml += button_line_tmp.format(buttons = button_buf)
            button_buf = ""
            current_line_char_num = 0
        current_line_char_num += len(district)
        button_buf += button_wxml_ele
        fileName = os.path.join(rootDir, city, f)
        targetFileName = city + '-**-' + f
        cmd = 'cp %s wximg/%s' % (fileName, targetFileName)
        #print(cmd)
        os.system(cmd)
    if current_line_char_num > 0:
        button_wxml += button_line_tmp.format(buttons = button_buf)
    if city == 'allcity':
        return ""
    citydes = citydesMap.get(city, "")
    if citydes == "":
        citydes = city 
    wxml = wxml_city_tmp.format(citydes = citydes, city = city, img = img_wxml, city_button = button_wxml)
    return wxml

 
wxml_city = ''
buttons = ''
button_buf = ''
current_line_char_num = 0
df = pd.read_excel('rank/城市排名.xlsx')
s = df['城市']
city_sorted = []
for city in s:
    for d in dirNames:
        if city in d and city not in city_sorted:
            city_sorted.append(d)
for d in dirNames:
    if not d in city_sorted:
        city_sorted.append(d)
dirNames = city_sorted
for city in dirNames:
    #try:
        if city == 'default' or city == 'allcity':
            continue
        if not os.path.isdir(os.path.join(rootDir, city)):
            continue
        getCityHTML(city)
        if city != 'allcity':
            wxml_city += makeWeixin(city)
        citydes = citydesMap.get(city, "")
        if citydes == "":
            citydes = city
        if current_line_char_num + len(citydes) > 10:
            buttons += button_line_tmp.format(buttons = button_buf)
            button_buf = ''
            current_line_char_num = 0
        current_line_char_num += len(citydes)
        button_buf += button_wxml_tmp.format(city=city,citydes=citydes)  
    #except Exception:
    #    print(Exception)
    #    pass
if current_line_char_num > 0:
   buttons += button_line_tmp.format(buttons = button_buf)
wxml = wxml_tmp.format(buttons = buttons, citydata =  wxml_city)
fp = open('/Users/alex/WeChatProjects/miniprogram-1/miniprogram/pages/fangjia/fangjia.wxml','w')
fp.write(wxml)
fp.close()
def exec(cmd):
    os.system(cmd)
getCityHTML('allcity')
exec('rsync -azP fig/ root@vps.yeshiwei.com:/var/www/html/fig')
exec('rsync -azP fangjia/ root@vps.yeshiwei.com:/var/www/html/fangjia')
