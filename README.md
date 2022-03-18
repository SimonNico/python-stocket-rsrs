# python-stocket-rsrs

## 根据光大证券的研报《基于阻力支撑相对强度（RSRS）的市场择时》实现的功能

#### 核心算法
```Pyhon
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

def get_slope_series(df):
    return [get_ols(df.low[i:i+N],df.high[i:i+N])[1] for i in range(M)]

def get_zscore(slope_series):
    mean=np.mean(slope_series)
    std=np.std(slope_series)
    return (slope_series[-1]-mean)/std

def get_timing_signal(df,series):
    current_dt = time.strftime("%Y-%m-%d", time.localtime())
    current_dt = datetime.strptime(current_dt, '%Y-%m-%d')
    start_dt3=datetime(current_dt.year,1,1)
    oneyeardf=df[df['date']>=start_dt3.strftime("%Y-%m-%d")].sort_values('date')
    ndata=df.tail(mean_day + mean_diff_day)
    today_MA=ndata.MA20[-1:].mean()
    # lastatr20=ndata.ATR20[-1:0].mean()
    before_MA=ndata.MA20[-mean_diff_day:].mean()
    high_low_data=df.tail(N)
    intercept,slope,r2=get_ols(high_low_data.low,high_low_data.high)
    
    maxdn,maxrate=DDN(oneyeardf)

    scoredf=df.tail(30)
    score,annualized_returns=SCORE(scoredf)
    series.append(slope)
    rsrs_score=get_zscore(series[-M:])*r2
    rst=''
    if rsrs_score>score_threshold and today_MA>before_MA:
        rst='建议买入'
    elif rsrs_score<-score_threshold:
        rst='建议卖出'
    else:
        rst='建议不做任何操作'
    return maxdn,maxrate,rst,rsrs_score,r2,today_MA,before_MA,score,annualized_returns


def run_rsrs(stock_codes):
    df=None
    current_dt = time.strftime("%Y-%m-%d", time.localtime())
    current_dt = datetime.strptime(current_dt, '%Y-%m-%d')
    previous_date  = current_dt - timedelta(days = day)
    predate=previous_date.strftime("%Y-%m-%d")
    sqlh=sqlHelper()
    sqlh.get_data('truncate table t_stock_rsrs')
    sqlh.get_data('truncate table t_stock_600data')
    codes=sqlh.get_data('select code,code_name from t_stock_hs300list')
    for stock in codes:
        try:
            series=[]
            df=get_data(stock[0])
            # df=get_data(stock)
            insert_600_data(df)
            series = get_slope_series(df)[:-1]
            maxdn,maxrate,surpose,rsrs_score,r2,m20,pre3M20,score,annualized_returns=get_timing_signal(df,series)
            lastrow=df.iloc[-1].tolist()
            # print(maxdn)
            # print(surpose)
            # print(lastrow)
            sqlh.update_data('insert into t_stock_rsrs(code,code_name,date,prehigh,prelow,preclose,m20,pre3m30,scope,r2,maxdval,maxrate,turn,amount,rsrs_suggest,score,annualized_returns)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[(stock[0],stock[1],lastrow[0],lastrow[3],lastrow[4],lastrow[5],m20,pre3M20,rsrs_score,r2,maxdn,maxrate,lastrow[10],lastrow[7],surpose,score,annualized_returns)])
        except Exception as ex:
            pass
            # print('Error',ex)
            # break
        continue
```
        
      
  * 需要在服务器做个定时任务跑，将数据写入数据库，然后定时任务跑发邮件的模块，建议每天早上发邮件
