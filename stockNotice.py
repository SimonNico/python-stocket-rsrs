import baostock as bs
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from stockIndex import DDN, MA, MACD,EOM,BBANDS

from pandas.io.formats.format import buffer_put_lines



N = 18 # 计算最新斜率 slope，拟合度 r2 参考最近 N 天
M = 600 # 计算最新标准分 zscore，rsrs_score 参考最近 M 天
score_threshold = 0.7 # rsrs 标准分指标阈值
# ma 择时参数
mean_day = 20 # 计算结束 ma 收盘价，参考最近 mean_day
mean_diff_day = 3 # 计算初始 ma 收盘价，参考(mean_day + mean_diff_day)天前，窗口为 mean_diff_day 的一段时间

day=1

stock_code="sh.601868"

score_threshold=0.7

slope_series=[]



df=pd.DataFrame(columns=['date,code,open','high','low','close','preclose','volume','amount','adjustflag','turn','tradestatus','pctChg','peTTM','pbMRQ','psTTM','pcfNcfTTM','isST'],dtype=float)

def get_data():
    current_dt = time.strftime("%Y-%m-%d", time.localtime())
    current_dt = datetime.strptime(current_dt, '%Y-%m-%d')
    start_date=datetime(current_dt.year-2,1,1)
    print(start_date.strftime("%Y-%m-%d"))
    data_list_all=[]
    bs.login()
    rs=bs.query_history_k_data_plus(stock_code,"date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",start_date.strftime("%Y-%m-%d"))
    while(rs.error_code=='0') & rs.next():
        data_list_all.append(rs.get_row_data())
    global df
    df=pd.DataFrame(data_list_all,columns=rs.fields)
    df=df.apply(pd.to_numeric,errors='ignore')
    df=MA(df,10)
    df=MA(df,20)
    df=MA(df,30)
    df=MA(df,60)
    df=MA(df,120)
    df=EOM(df,30)
    df=BBANDS(df,60)
    df=df.iloc[::-1]
    # df.to_csv("D:/3.csv", encoding="gbk", index=False)
    bs.logout()



# 对输入的自变量每日最低价 x(series) 和因变量每日最高价 y(series) 建立 OLS 回归模型,返回元组(截距,斜率,拟合度)
# R2 统计学线性回归决定系数，也叫判定系数，拟合优度。
# R2 范围 0 ~ 1，拟合优度越大，自变量对因变量的解释程度越高，越接近 1 越好。
def get_ols(x,y):
    if x.size==0:
        return 0,0,0
    try:
        slope, intercept = np.polyfit(x, y, 1)
        r2 = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
    except np.RankWarning:
        slope, intercept,r2=0,0,0
    return (intercept, slope, r2)

def get_slope_series():
    # current_dt = time.strftime("%Y-%m-%d", time.localtime())
    # current_dt = datetime.strptime(current_dt, '%Y-%m-%d')
    # previous_date=current_dt-timedelta(days=day)
    # start_time=current_dt-timedelta(days=M+N)
    # bs.login()
    # data=bs.query_history_k_data_plus(stock_code,"high,low",start_time.strftime("%Y-%m-%d"))
    # data_list=[]
    # while(data.error_code=='0') & data.next():
    #     data_list.append(data.get_row_data())
    # result=pd.DataFrame(data_list,columns=data.fields,dtype=float)

    # bs.logout()
    # # result.to_csv("D:/1.csv", encoding="gbk", index=False)
    global df
    result=df
    return [get_ols(result.low[i:i+N],result.high[i:i+N])[1] for i in range(M)]

def get_zscore(slope_series):
    mean=np.mean(slope_series)
    std=np.std(slope_series)
    return (slope_series[-1]-mean)/std


def get_timing_signal():
    current_dt = time.strftime("%Y-%m-%d", time.localtime())
    current_dt = datetime.strptime(current_dt, '%Y-%m-%d')
    # previous_date  = current_dt - timedelta(days = day)
    # start_dt1=current_dt-timedelta(days=mean_day+mean_diff_day)
    # start_dt2=current_dt-timedelta(days=N)
    start_dt3=datetime(current_dt.year-1,1,1)
    # bs.login()
    # close_data=bs.query_history_k_data_plus(stock_code,"close",start_dt1.strftime("%Y-%m-%d"))
    # close_arr=[]
    # while(close_data.error_code=='0') & close_data.next():
    #     close_arr.append(close_data.get_row_data())
    # close_result=pd.DataFrame(close_arr,columns=close_data.fields,dtype=float)
    global df
    
    oneyeardf=df[df['date']>=start_dt3.strftime("%Y-%m-%d")].sort_values('date')
    # ndata.to_csv("D:/4.csv", encoding="gbk", index=False)
    ndata=df.head(mean_day + mean_diff_day)
    ndata=ndata[::-1]
    today_MA=ndata.MA20[-1:].mean()
    before_MA=ndata.MA20[-mean_diff_day:].mean()
    high_low_data=df.head(N)
    # high_low_data.to_csv("D:/5.csv", encoding="gbk", index=False)
    intercept,slope,r2=get_ols(high_low_data.low,high_low_data.high)
    maxdn,maxrate,maxvalue,fd=DDN(oneyeardf)
    # print(slope)
    # print(r2)
    # print(today_MA)
    # print(before_MA)
    # print(ndata)
    # print(ndata.MA20[-1:])
    # print(ndata.MA20[-3:])
    # print(oneyeardf)
    print(maxdn)
    print(maxrate)
    # print(oneyeardf)

    slope_series.append(slope)
    rsrs_score=get_zscore(slope_series[-M:])*r2
    # print(slope_series)
    print(rsrs_score)
    if rsrs_score>score_threshold and today_MA>before_MA:
        return "Buy"
    elif rsrs_score<-score_threshold:
        return "Sell"
    else:
        return "Keep"

if __name__ == '__main__':
    get_data()
    slope_series = get_slope_series()[:-1]
    print(get_timing_signal())
    