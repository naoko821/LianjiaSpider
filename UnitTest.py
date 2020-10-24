from common import read
data1 = read('北京')
x=data1.groupby(['成交时间']).size()
x.index
date = list(x.index)
date.sort()
print(date[-10:])