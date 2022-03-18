import requests
import time
from datetime import datetime
from interval import Interval
from threading import Timer

sina_realtime_url='https://hq.sinajs.cn/list='
def get_data(code):
    res=requests.get(sina_realtime_url+code)
    print(res.text.replace('="',',').split(',')[1:-1])

def schedule_get_data():
    global t1
    now_localtime = time.strftime("%H:%M:%S", time.localtime())
    now_localtime = time.strftime("%H:%M:%S", time.localtime())
# 当前时间（以时间区间的方式表示）
    now_time = Interval(now_localtime, now_localtime)

    time_interval_one = Interval("09:30:00", "11:30:00")
    time_interval_two = Interval("13:00:00", "14:10:00")
    get_data('sz000100')
    t1=Timer(5,schedule_get_data)
    if now_time in time_interval_one or now_localtime in time_interval_two:
        t1.start()
    else:
        t1.cancel()
        
    
       

if __name__=='__main__':
    schedule_get_data()
