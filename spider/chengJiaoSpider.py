# -*- coding: utf-8 -*-
import random
import re
import requests
import sys
import lxml
import datetime
import time
import os
from multiprocessing import Pool
from bs4 import BeautifulSoup
from generate_excle import generate_excle
from AgentAndProxies import hds
from AgentAndProxies import GetIpProxy
from model.ElementConstant import ElementConstant
from setting import cityList
from checkStatus import check

cityMap = {'北京':'bj','上海':'sh', '杭州':'hz', '深圳':'sz', '广州':'gz', 
           '宁波':'nb', '长沙':'cs', '厦门':'xm', '成都':'cd', '合肥':'hf',
          '石家庄':'sjz', '重庆':'cq', '西安':'xa', '青岛':'qd', '南京':'nj',
          '苏州':'su','大连':'dl', '无锡':'wx', '武汉':'wh', '保定':'bd', '温州':'wz',
            '南通':'nt', '廊坊':'lf', '东莞':'dg','济南':'jn', '长春':'cc'}
districtMap = {'大连':['甘井子', '沙河口', '西岗', '金州', '中山', '开发区', '高新园区', '普兰店', '旅顺口'],
                '济南':['历下', '天桥', '市中', '槐荫', '高新', '长清', '历城', '章丘'],
            '长春':['九台区',
 '二道区',
 '农安县',
 '净月区',
 '南关区',
 '双阳区',
 '宽城区',
 '德惠市',
 '朝阳区',
 '榆树市',
 '汽车产业开发区',
 '经开北区',
 '经开区',
 '绿园区',
 '高新北区',
 '高新区'], '深圳':['南山区', '福田区', '宝安区', '龙华区', '罗湖区', '光明区', '盐田区', '龙岗区', '坪山区', '大鹏新区']}

class chengJiaoInfo:
    # 初始化构造函数
    def __init__(self, city, url = None):
        self.city = city
        self.elementConstant = ElementConstant()
        self.getIpProxy = GetIpProxy()
#        self.url = "https://bj.lianjia.com/ershoufang/pg{}/"
        if url == None:
            self.url = "https://%s.lianjia.com/chengjiao/pg{}/"%cityMap[self.city]
        else:
            self.url = url
        self.infos = {}
        self.proxyServer = ()
        # 传参使用进行excle生成
        self.generate_excle = generate_excle()
        self.elementConstant = ElementConstant()
    # 生成需要生成页数的链接
    def generate_allurl(self, user_in_nub):
        for url_next in range(1, int(user_in_nub) + 1):
            self.page = url_next
            yield self.url.format(url_next)

    # 开始函数
    def start(self):
        self.generate_excle.addSheetExcle(u'在售列表')
        user_in_nub = 100#input('输入生成页数：')
        for i in self.generate_allurl(user_in_nub):
            try:
                print('page', i)
                url_count = self.get_allurl(i)
                while url_count == 0:
                    print("error get item url.", i)
                    self.proxyServer = self.getIpProxy.get_random_ip()
                    url_count = self.get_allurl(i)
                if self.page % 5 == 0:
                    self.saveResult()
            except Exception as e:
                print(i, e, 'failed')
        self.saveResult()

    def saveResult(self):
        date = str(datetime.datetime.now().date())
        dirName = 'data/chengjiao-%s'%self.city
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        self.generate_excle.saveExcle('%s/%s-%s.xls'%(dirName, date, self.city.split('/')[-1]))
    
    def get_allurl(self, generate_allurl):
        geturl = self.requestUrlForRe(generate_allurl)
        url_count = 0
        if geturl.status_code == 200:
            # 提取title跳转地址　对应每个商品
            re_set = re.compile('<li.*?<a.*?class="img.*?".*?href="(.*?)"')
            re_get = re.findall(re_set, geturl.text)
            url_count = len(re_get)
            for index in range(len(re_get)):
                print re_get[index]
                url_status = self.open_url(re_get[index], index)
                while url_status == False:
                    self.proxyServer = self.getIpProxy.get_random_ip()
                    url_status = self.open_url(re_get[index], index)
                print(re_get[index])
        return url_count

    def open_url(self, re_get, index):
        print(re_get, index)
        res = self.requestUrlForRe(re_get)
        if res.status_code == 200:
            if 'sec_tech@ke.com' in res.text:
                return False
            soup = BeautifulSoup(res.text, 'lxml')
            self.infos['网址'] = re_get
            self.infos['标题'] = soup.title.text.split('_')[0]
            self.infos['售价(万)'] = soup.find(class_='dealTotalPrice').text
            self.infos['每平方售价'] = soup.find(class_='record_detail').text.split('元')[0][2:]
            partent = re.compile('<li><span class="label">(.*?)</span>(.*?)</li>')
            result = re.findall(partent, res.text)
            for item in result:
                if item[0] == '建成年代':
                    self.infos['建成时间：年'] = item[1].strip()
                else:
                    self.infos[item[0]] = item[1].strip()
                  
            partent = re.compile('<i>></i>(.*?)</a>')
            result = re.findall(partent, res.text)
            self.infos['所属下辖区']=result[1].split('>')[1].split('二手房')[0]
            self.infos['所属商圈']=result[2].split('>')[1].split('二手房')[0]
            self.infos['所属小区']=result[3].split('>')[1].split('二手房')[0]
            msg = soup.find(class_='msg').contents
            result = [(a.contents[1], a.contents[0].text, ) for a in msg]
            for item in result:
                if item[0] == '建成年代':
                    self.infos['建成时间：年'] = item[1].strip()
                else:
                    self.infos[item[0]] = item[1].strip()
            self.infos['成交时间'] = '-'.join(soup.find(class_='wrapper').contents[1].text.split()[0].split('.'))
            row = index + (self.page - 1) * 30
            #self.infos['序号'] = row + 1
            self.infos['城市'] = self.city
            print('row:' + str(row))
            if row == 0:
                for index_item in self.elementConstant.data_constant.keys():
                    self.generate_excle.writeExclePositon(0, self.elementConstant.data_constant.get(index_item),
                                                          index_item)

                self.wirte_source_data(1)

            else:
                row = row + 1
                self.wirte_source_data(row)
        return True

    # 封装统一request请求,采取动态代理和动态修改User-Agent方式进行访问设置,减少服务端手动暂停的问题
    def requestUrlForRe(self, url):

        try:
            if len(self.proxyServer) == 0:
                tempProxyServer = self.getIpProxy.get_random_ip()
            else:
                tempProxyServer = self.proxyServer
            proxy_dict = {
                tempProxyServer[0]: tempProxyServer[1]
            }
            tempUrl = requests.get(url, headers=hds[random.randint(0, len(hds) - 1)], proxies=proxy_dict)
            code = tempUrl.status_code
            #print tempUrl.text.decode('gbk')
            if code >= 200 or code < 300:
                self.proxyServer = tempProxyServer
                return tempUrl
            else:
                self.proxyServer = self.getIpProxy.get_random_ip()
                return self.requestUrlForRe(url)
        except Exception as e:
            self.proxyServer = self.getIpProxy.get_random_ip()
            s = requests.session()
            s.keep_alive = False
            return self.requestUrlForRe(url)

    # 源数据生成,写入excle中,从infos字典中读取数据,放置到list列表中进行写入操作,其中可修改规定写入格式
    def wirte_source_data(self, row):
        for itemKey in self.infos.keys():
            #print(itemKey + ':' + str(self.infos.get(itemKey)))

            item_valus = self.infos.get(itemKey)
            tempItemKey = self.elementConstant.unit_check_name(itemKey.encode('utf-8'))
            count = self.elementConstant.data_constant.get(tempItemKey)
            print tempItemKey, self.elementConstant.data_constant.get(tempItemKey), item_valus
            if tempItemKey != None and count != None:

                self.generate_excle.writeExclePositon(row,
                                                      self.elementConstant.data_constant.get(tempItemKey),
                                                      item_valus)

def getXiaoqu(param):
    cityCode = param[0]
    xiaoqu = param[1]
    url = 'https://%s.lianjia.com/chengjiao/pg{}rs%s/'%(cityCode, xiaoqu)
    spider = chengJiaoInfo('all%s/%s'%(cityCode, xiaoqu), url)
    spider.start()    
        
def getAllXiaoqu(city):
    cityCode = cityMap[city]
    xiaoquList = open('xiaoqu/%sxiaoqu.txt'%cityCode).read().split()
    targetDir = 'data/chengjiao-all%s/'%cityCode
    if os.path.exists(targetDir):
        done = os.listdir(targetDir)
        xiaoquList = list(set(xiaoquList) - set(done))
    print(len(xiaoquList), cityCode)
    p = Pool()
    paramList = zip([cityCode] * len(xiaoquList), xiaoquList)
    p.map(getXiaoqu, paramList)
    
def getAllDistrict(city):
    districtList = districtMap[city]
    print(districtList)
    cityCode = cityMap[city]
    paramList = zip([cityCode] * len(districtList), districtList)
    for p in paramList:
        getXiaoqu(p)  
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        city_list = cityList
        done, unfinished = check()
        for city in cityMap.keys():
            if not city in city_list:
                city_list.append(city)
        city_list_tmp = city_list
        city_list = []
        for city in city_list_tmp:
            if city in unfinished:
                city_list.append(city)
        def getCity(city):
            spider = chengJiaoInfo(city)
            spider.start()
        for city in city_list:
            getCity(city)
    elif len(sys.argv) == 2:
        area = sys.argv[1]
        url = 'https://bj.lianjia.com/chengjiao/pg{}rs%s/'%area
        spider = chengJiaoInfo(area, url)
        spider.start()
    elif len(sys.argv) == 3:
        city = sys.argv[1]
        area = sys.argv[2]
        if area =='latest':
            url = 'https://%s.lianjia.com/chengjiao/pg{}/'%(cityMap[city])
            print(url)
            spider = chengJiaoInfo(city, url)
            spider.start()
        elif area == 'all':
            getAllXiaoqu(city)
        elif area == 'alldis':
            getAllDistrict(city)
        else:
            url = 'https://%s.lianjia.com/chengjiao/pg{}rs%s/'%(cityMap[city], area)
            spider = chengJiaoInfo(area, url)
            spider.start()
        
