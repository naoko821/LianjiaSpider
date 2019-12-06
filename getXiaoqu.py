from common import read
import pandas as pd
import sys
city = sys.argv[1]
df = read(city)
xiaoqu = df['小区'].unique()
fp=open('xiaoqu.txt', 'w')
for x in xiaoqu:
    fp.write(x+'\n')
fp.close()
