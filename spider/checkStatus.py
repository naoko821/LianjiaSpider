import os
from setting import cityList
import datetime
def check():
    recent_dates = []
    today = datetime.datetime.today().date()
    for i in range(0, 3):
        recent_dates.append(str(today - datetime.timedelta(i)))
    done = []
    unfinished = []
    for city in cityList:
        flag = False
        for d in recent_dates:
            filename = "data/chengjiao-%s/%s-%s.xls"%(city, d, city)
            if os.path.exists(filename):
                done.append(city)
                flag = True
        if flag == False:
            unfinished.append(city)
    return done, unfinished

if __name__ == "__main__":
    done, unfinished = check()
    print('done', done)
    print('unfinished', unfinished)
