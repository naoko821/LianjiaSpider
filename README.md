# 链家 （python）爬虫  成交数据 及 在售数据 爬取

依赖包 lxml requests BeautifulSoup xlwt xlrd Bs4

mac or linux :

sudo pip2.7 install lxml requests BeautifulSoup xlwt xlrd Bs4

windows:

pip2.7 install lxml requests BeautifulSoup xlwt xlrd Bs4

分析程序需要安装anaconda3.

项目目录说明:

HomeLinkTest : Android 工程（用于破解链家App签名验证内容）

jsonSource: 链家客户端json传内容样本，包含（成交商品列表页，成交商品详情页，成交商品更多内容页）（在售商品列表页，在售商品详情页，在售商品更多内容页）

spider：链家爬虫脚本（python脚本）（爬取PC端在线数据，移动端在售数据和成交数据）

爬虫脚本基于python2.7，jupyter-notebook基于python3

#前言：链家数据爬虫，本文采用两种方式

1.常见的分析PC端HTML进行数据爬取（简单实现在售数据爬取，成交数据需要在移动端查看）

2.破解链家移动端签名密钥，使用客户端接口进行爬取（在售数据及成交数据爬取）

实现功能：

一. web界面爬取

爬取web界面在售内容 https://bj.lianjia.com/ershoufang/ 仅爬取在售内容

```
python2.7 LianjiaSpider/spider/salingInfoSpider.py

```

爬取web界面成交内容 https://bj.lianjia.com/chengjiao/

```
python2.7 LianjiaSpider/spider/chengJiaoSpider.py

```

二.移动端数据爬取（在售，成交）

基于链家app:https://bj.lianjia.com/ 针对其签名校验进行破解

获取对应的json内容，进行自动爬取（仅做技术交流，请勿进行商业应用或其他侵权行为）

在售数据爬取：
```
python2.7 LianjiaSpider/spider/zaishou/zaiShouSpider.py
```
成交数据爬取：
```
python2.7 LianjiaSpider/spider/zaishou/chengJiaoJiaSpider.py
```


在售及成交数据自动爬取：
```
python2.7 LianjiaSpider/spider/Spider_Thread_Manager.py
```

三.jupyter-notebook分析

安装anaconda3, 在终端中运行jupyter-notebook 然后在弹出网页中打开analysis.ipynb或者 单价因子.ipynb

四.爬取小区数据并作图

```
python3 plotArea.py [city] [area]
```

然后在 fig/default目录里查看图片。

Copyright 2016 Square, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
