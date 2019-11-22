# -*- coding: utf-8 -*-
import random
import re
import requests
import sys
import lxml
import datetime
import os
from multiprocessing import Pool
from bs4 import BeautifulSoup
from generate_excle import generate_excle
from AgentAndProxies import hds
from AgentAndProxies import GetIpProxy
from model.ElementConstant import ElementConstant
from pypinyin import lazy_pinyin
cityMap = {'天津':'tj'}
districtMap = {'大连':['甘井子', '沙河口', '西岗', '金州', '中山', '开发区', '高新园区', '普兰店', '旅顺口'],
'天津': ['和平',
 '南开',
 '河西',
 '河北',
 '河东',
 '红桥',
 '西青',
 '北辰',
 '东丽',
 '津南',
 '塘沽开发区',
 '武清',
 '滨海新区',
 '宝坻',
 '蓟州',
 '海河教育园区',
 '静海']}


class chengJiaoInfo:
    # 初始化构造函数
    def __init__(self, city, url = None):
        self.city = city
        self.elementConstant = ElementConstant()
        self.getIpProxy = GetIpProxy()
        if url == None:
            self.url = "https://%s.ke.com/chengjiao/pg{}/"%cityMap[self.city]
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
                count = self.get_allurl(i)
                print(i)
                if count == 0:
                    break
            except Exception as e:
                print(i, e, 'failed')
        date = str(datetime.datetime.now().date())
        dirName = 'data/chengjiao-%s'%self.city
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        self.generate_excle.saveExcle('%s/%s-%s.xls'%(dirName, date, self.city.split('/')[-1]))

    def get_allurl(self, generate_allurl):
        geturl = self.requestUrlForRe(generate_allurl)
        count = 0
        if geturl.status_code == 200:
            # 提取title跳转地址　对应每个商品
            re_set = re.compile('<li.*?<a.*?class="img.*?".*?href="(.*?)"')
            re_get = re.findall(re_set, geturl.text.replace('\n', ''))
            for index in range(len(re_get)):
                print re_get[index]
                if re_get[index].startswith('http'):
                    count += 1
                    self.open_url(re_get[index], index)
                print(re_get[index])
        return count

    def open_url(self, re_get, index):
        print(re_get, index)
        res = self.requestUrlForRe(re_get)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            self.infos['网址'] = re_get
            self.infos['标题'] = soup.title.text.split('_')[0]
            self.infos['售价(万)'] = soup.find(class_='dealTotalPrice').text.strip()
            self.infos['每平方售价'] = soup.find(class_='record_detail').text.split('元')[0].strip()[2:]
            partent = re.compile('<li><span class="label">(.*?)</span>(.*?)</li>')
            result = re.findall(partent, res.text)
            for item in result:
                if item[0] == '建成年代':
                    self.infos['建成时间：年'] = item[1].strip()
                else:
                    self.infos[item[0]] = item[1].strip()

            ele=soup.find(class_='fl l-txt')
            result = [a.text for a in ele.find_all('a')]
            self.infos['所属下辖区']=result[2].split('二手房')[0]
            self.infos['所属商圈']=result[3].split('二手房')[0]
            self.infos['所属小区']=result[4].split('二手房')[0]
            msg = soup.find(class_='msg')
            result = []
            for x in msg.find_all('span'):
                fields = x.text.replace(" ","").split('\n')
                con = []
                for c in fields:
                    if c != '':
                        con.append(c)
                result.append(con)
            for item in result:
                if item[1] == '建成年代':
                    self.infos['建成时间：年'] = item[0].strip()
                else:
                    self.infos[item[1]] = item[0].strip()
            self.infos['成交时间'] = '-'.join(soup.find('strong').text.strip().split('.'))
            row = index + (self.page - 1) * 30
            #infos['序号'] = row + 1
            self.infos['城市'] = self.city
            print('row:' + str(row))
            print '小区', self.infos['所属小区']
            if row == 0:
                for index_item in self.elementConstant.data_constant.keys():
                    self.generate_excle.writeExclePositon(0, self.elementConstant.data_constant.get(index_item),
                                                          index_item)

                self.wirte_source_data(1)

            else:
                row = row + 1
                self.wirte_source_data(row)
        return self.infos

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
            #print itemKey + ':' + str(self.infos.get(itemKey))

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
    url = 'https://%s.ke.com/chengjiao/pg{}rs%s/'%(cityCode, xiaoqu)
    spider = chengJiaoInfo('all%s/%s'%(cityCode, xiaoqu), url)
    spider.start()    

def getTJDistrict(param):
    cityCode = param[0]
    district = ''.join(lazy_pinyin(param[1].decode('utf8')))
    url = 'https://%s.ke.com/chengjiao/%s/pg{}rs/'%(cityCode, district)
    spider = chengJiaoInfo('all%s/%s'%(cityCode, district), url)
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
    cityCode = cityMap[city]
    paramList = zip([cityCode] * len(districtList), districtList)
    p = Pool()
    if city == '天津':
        p.map(getTJDistrict, paramList)
    else:
        p.map(getXiaoqu, paramList) 
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        city_list = cityMap.keys()
        def getCity(city):
            spider = chengJiaoInfo(city)
            spider.start()
        p = Pool()
        p.map(getCity, city_list)
    elif len(sys.argv) == 2:
        area = sys.argv[1]
        url = 'https://bj.ke.com/chengjiao/pg{}rs%s/'%area
        spider = chengJiaoInfo(area, url)
        spider.start()
    elif len(sys.argv) == 3:
        city = sys.argv[1]
        area = sys.argv[2]
        if area =='latest':
            url = 'https://%s.ke.com/chengjiao/pg{}/'%(cityMap[city])
            print(url)
            spider = chengJiaoInfo(city, url)
            spider.start()
        elif area == 'all':
            getAllXiaoqu(city)
        elif area == 'alldis':
            getAllDistrict(city)
        else:
            url = 'https://%s.ke.com/chengjiao/pg{}rs%s/'%(cityMap[city], area)
            spider = chengJiaoInfo(area, url)
            spider.start()
        
