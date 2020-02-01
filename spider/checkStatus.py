import os
from setting import cityList
import datetime
def check():
    today = str(datetime.datetime.today().date())
    done = []
    unfinished = []
    for city in cityList:
        filename = "data/chengjiao-%s/%s-%s.xls"%(city, today, city)
        print(filename)
        if os.path.exists(filename):
            done.append(city)
        else:
            unfinished.append(city)
    return done, unfinished

if __name__ == "__main__":
    done, unfinished = check()
    print('done', done)
    print('unfinished', unfinished)
