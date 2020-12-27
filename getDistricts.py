from common import read
import pandas as pd
import sys
city = sys.argv[1]
df = read(city)
districts = df['下辖区'].unique()
print(districts)
