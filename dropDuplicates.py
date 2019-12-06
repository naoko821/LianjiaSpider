from common import read
import pandas as pd
import sys
city = sys.argv[1]
df = read(city)
df.to_csv(city+'.csv')
