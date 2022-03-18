#-*- codig:utf-8 -*-

import numpy as np
from pandas import *
from math import *
#pandas 版本为1.3.4
#老式的pd.rolling_mean\pd.ewma等不能用 改用新的方式
# 移动平均
def MA(df,n):
    MA=Series(df['close'].rolling(n).mean(),name='MA'+str(n))
    df=df.join(MA)
    return df

#指数移动平均EMA
def EMA(df,n):
    EMA=Series(df['close'].ewm(span=2,min_periods=n-1,ignore_na=True,adjust=True).mean(),name='EMA'+str(n))
    df=df.join(EMA)
    return df

#动量
def MOM(df,n):
    M=Series(df['close'].diff(n),name='Monentum'+str(n))
    df=df.join(M)
    return df

#变化率
def ROC(df,n):
    M=df['close'].diff(n-1)
    M=df['close'].shift(n-1)
    ROC=Series(M/n,name='ROC'+str(n))
    df=df.join(ROC)
    return df

#均幅指标
def ATR(df,n):
    i=0
    TR_l=[0]
    while i<df.index[-1]:
        TR=max(df._get_value(i+1,'high'),df._get_value(i,'close'))- min(df._get_value(i + 1, 'low'), df._get_value(i, 'close'))
        TR_l.append(TR)
        i=i+1
    TR_s=Series(TR_l)
    ATR=Series(TR_s.ewm(span=n,min_periods=n,adjust=True,ignore_na=True).mean(),name='ATR'+str(n))
    df=df.join(ATR)
    return df

#布林线
def BBANDS(df,n):
    MA=Series(df['close'].rolling(n).mean())
    MSD=Series(df['close'].rolling(n).std())
    b1=4*MSD/MA
    B1=Series(b1,name='BollingB'+str(n))
    df=df.join(B1)
    b2=(df['close']-MA+2*MSD)/(4*MSD)
    B2=Series(b2,name='BollingU'+str(n))
    df=df.join(B2)
    return df

#转折、支撑、阻力点
def PPSR(df):
    PP=Series((df['high']+df['low']+df['close'])/3)
    R1=Series(2*PP-df['low'])
    S1=Series(2*PP-df['high'])
    R2=Series(PP+df['high']-df['low'])
    S2=Series(PP-df['high']+df['low'])
    R3=Series(df['high']+2*(PP-df['low']))
    S3=Series(df['low']-2*(df['high']-PP))
    psr = {'PP':PP, 'R1':R1, 'S1':S1, 'R2':R2, 'S2':S2, 'R3':R3, 'S3':S3}
    PSR = DataFrame(psr)
    df = df.join(PSR)
    return df

#随机振荡器 K线
def STOK(df):
    SOK=Series((df['close'] - df['low']) / (df['high'] - df['low']), name = 'SOK')
    df=df.join(SOK)
    return df

# 随机振荡器 D线
def STO(df,n):
    SOK=Series((df['close'] - df['low']) / (df['high'] - df['low']), name = 'SOK')
    SOD=Series(SOK.ewm(span=n,min_periods=n-1,adjust=True,ignore_na=True).mean(), name = 'SOD' + str(n))
    df=df.join(SOD)
    return df

# 三重指数平滑平均线
def TRIX(df,n):
    EX1=df['close'].ewm(span=n,min_periods=n-1,adjust=True,ignore_na=True).mean()
    EX2=EX1.ewm(span=n,min_periods=n-1,adjust=True,ignore_na=True).mean()
    EX3=EX2.ewm(span=n,min_periods=n-1,adjust=True,ignore_na=True).mean()
    i=0
    ROC_l = [0]
    while i + 1 <= df.index[-1]:
        ROC = (EX3[i + 1] - EX3[i]) / EX3[i]
        ROC_l.append(ROC)
        i = i + 1
    Trix = Series(ROC_l, name = 'Trix' + str(n))
    df = df.join(Trix)
    return df

#平均定向运动指数
def ADX(df, n, n_ADX):
    i = 0
    UpI = []
    DoI = []
    while i + 1 <= df.index[-1]:
        UpMove = df._get_value(i + 1, 'high') - df._get_value(i, 'high')
        DoMove = df._get_value(i, 'low') - df._get_value(i + 1, 'low')
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else: UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else: DoD = 0
        DoI.append(DoD)
        i = i + 1
    i = 0
    TR_l = [0]
    while i < df.index[-1]:
        TR = max(df._get_value(i + 1, 'high'), df._get_value(i, 'close')) - min(df._get_value(i + 1, 'low'), df._get_value(i, 'close'))
        TR_l.append(TR)
        i = i + 1
    TR_s = Series(TR_l)
    ATR = Series(TR_s.ewm(span=n,min_periods=n,adjust=True,ignore_na=True).mean())
    UpI = Series(UpI)
    DoI = Series(DoI)
    PosDI = Series(UpI.ewm(span = n, min_periods = n - 1,adjust=True,ignore_na=True).mean()/ ATR)
    NegDI = Series(DoI.ewm(span = n, min_periods = n - 1,adjust=True,ignore_na=True).mean()/ ATR)
    ADX = Series((abs(PosDI - NegDI) / (PosDI + NegDI)).ewm(span = n_ADX, min_periods = n_ADX - 1,adjust=True,ignore_na=True).mean(), name = 'ADX' + str(n) + '_' + str(n_ADX))
    df = df.join(ADX)
    return df

#MACD
def MACD(df, n_fast, n_slow):
    EMAfast = Series(df['close'].ewm(span = n_fast, min_periods = n_slow - 1).mean())
    EMAslow = Series(df['close'].ewm(span = n_slow, min_periods = n_slow - 1).mean())
    MACD = Series(EMAfast - EMAslow, name = 'MACD' + str(n_fast) + '_' + str(n_slow))
    MACDsign = Series(MACD.ewm(span=9,min_periods=8,adjust=True,ignore_na=True).mean(), name = 'MACDsign' + str(n_fast) + '_' + str(n_slow))
    MACDdiff = Series(MACD - MACDsign, name = 'MACDdiff' + str(n_fast) + '_' + str(n_slow))
    df = df.join(MACD)
    df = df.join(MACDsign)
    df = df.join(MACDdiff)
    return df

#.梅斯线（高低价趋势反转）
def MassI(df):
    Range = df['high'] - df['low']
    EX1 =Range.ewm(span = 9, min_periods = 8,adjust=True,ignore_na=True).mean()
    EX2 =EX1.ewm(span = 9, min_periods = 8,adjust=True,ignore_na=True).mean()
    Mass = EX1 / EX2
    MassI = Series(Mass.rolling(25).mean(), name = 'Mass Index')
    df = df.join(MassI)
    return df

#涡旋指标
def Vortex(df, n):
    i = 0
    TR = [0]
    while i < df.index[-1]:
        Range = max(df._get_value(i + 1, 'high'), df._get_value(i, 'close')) - min(df._get_value(i + 1, 'low'), df._get_value(i, 'close'))
        TR.append(Range)
        i = i + 1
    i = 0
    VM = [0]
    while i < df.index[-1]:
        Range = abs(df._get_value(i + 1, 'high') - df._get_value(i, 'low')) - abs(df._get_value(i + 1, 'low') - df._get_value(i, 'high'))
        VM.append(Range)
        i = i + 1
    VI = Series(Series(VM).rolling(n).mean()  / Series(TR).rolling(n).mean(), name = 'Vortex_' + str(n))
    df = df.join(VI)
    return df

# KST振荡器
def KST(df, r1, r2, r3, r4, n1, n2, n3, n4):
    M = df['close'].diff(r1 - 1)
    N = df['close'].shift(r1 - 1)
    ROC1 = M / N
    M = df['close'].diff(r2 - 1)
    N = df['close'].shift(r2 - 1)
    ROC2 = M / N
    M = df['close'].diff(r3 - 1)
    N = df['close'].shift(r3 - 1)
    ROC3 = M / N
    M = df['close'].diff(r4 - 1)
    N = df['close'].shift(r4 - 1)
    ROC4 = M / N
    KST = Series(ROC1.rolling(n1).mean() + ROC2.rolling(n2).mean()* 2 +ROC3.rolling(n3).mean()* 3 +ROC4.rolling(n4).mean()*4, name = 'KST' + str(r1) + '_' + str(r2) + '_' + str(r3) + '_' + str(r4) + '_' + str(n1) + '_' + str(n2) + '_' + str(n3) + '_' + str(n4))
    df = df.join(KST)
    return df

# 相对强度指标
def RSI(df, n):
    i = 0
    UpI = [0]
    DoI = [0]
    while i + 1 <= df.index[-1]:
        UpMove = df._get_value(i + 1, 'high') - df._get_value(i, 'high')
        DoMove = df._get_value(i, 'low') - df._get_value(i + 1, 'low')
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else: UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else: DoD = 0
        DoI.append(DoD)
        i = i + 1
    UpI = Series(UpI)
    DoI = Series(DoI)
    PosDI = Series(UpI.ewm(span=n,min_periods=n-1,adjust=True,ignore_na=True).mean())
    NegDI = Series(DoI.ewm(span=n,min_periods=n-1,adjust=True,ignore_na=True).mean())
    RSI = Series(PosDI / (PosDI + NegDI), name = 'RSI' + str(n))
    df = df.join(RSI)
    return df

#真实强度指标
def TSI(df, r, s):
    M = Series(df['close'].diff(1))
    aM = abs(M)
    EMA1 = Series(M.ewm(span=r,min_periods=r-1,adjust=True,ignore_na=True).mean())
    aEMA1 = Series(aM.ewm(span=r,min_periods=r-1,adjust=True,ignore_na=True).mean())
    EMA2 = Series(EMA1.ewm(span=s,min_periods=s-1,adjust=True,ignore_na=True).mean())
    aEMA2 = Series(aEMA1.ewm(span=s,min_periods=s-1,adjust=True,ignore_na=True).mean())
    TSI = Series(EMA2 / aEMA2, name = 'TSI' + str(r) + '_' + str(s))
    df = df.join(TSI)
    return df

#吸筹/派发指标
def ACCDIST(df, n):
    ad = (2 * df['close'] - df['high'] - df['low']) / (df['high'] - df['low']) * df['volume']
    M = ad.diff(n - 1)
    N = ad.shift(n - 1)
    ROC = M / N
    AD = Series(ROC, name = 'Acc/Dist_ROC' + str(n))
    df = df.join(AD)
    return df

#佳庆指标CHAIKIN振荡器
def Chaikin(df):
    ad = (2 * df['close'] - df['high'] - df['low']) / (df['high'] - df['low']) * df['volume']
    Chaikin = Series(ad.ewm(span = 3, min_periods = 2,adjust=True,ignore_na=True).mean() -ad.ewm(span = 10, min_periods = 9,adjust=True,ignore_na=True).mean(), name = 'Chaikin')
    df = df.join(Chaikin)
    return df

# 资金流量与比率指标
def MFI(df, n):
    PP = (df['high'] + df['low'] + df['close']) / 3
    i = 0
    PosMF = [0]
    while i < df.index[-1]:
        if PP[i + 1] > PP[i]:
            PosMF.append(PP[i + 1] * df._get_value(i + 1, 'volume'))
        else:
            PosMF.append(0)
        i = i + 1
    PosMF = Series(PosMF)
    TotMF = PP * df['volume']
    MFR = Series(PosMF / TotMF)
    MFI = Series(MFR.rolling(n).mean(), name = 'MFI' + str(n))
    df = df.join(MFI)
    return df

#能量潮指标
def OBV(df, n):
    i = 0
    OBV = [0]
    while i < df.index[-1]:
        if df._get_value(i + 1, 'close') - df._get_value(i, 'close') > 0:
            OBV.append(df._get_value(i + 1, 'volume'))
        if df._get_value(i + 1, 'close') - df._get_value(i, 'close') == 0:
            OBV.append(0)
        if df._get_value(i + 1, 'close') - df._get_value(i, 'close') < 0:
            OBV.append(-df._get_value(i + 1, 'volume'))
        i = i + 1
    OBV = Series(OBV)
    OBV_ma = Series(OBV.rolling(n).mean(), name = 'OBV' + str(n))
    df = df.join(OBV_ma)
    return df

# 强力指数指标
def FORCE(df, n):
    F = Series(df['close'].diff(n) * df['volume'].diff(n), name = 'Force' + str(n))
    df = df.join(F)
    return df

# 简易波动指标
def EOM(df, n):
    EoM = (df['high'].diff(1) + df['low'].diff(1)) * (df['high'] - df['low']) / (2 * df['volume'])
    Eom_ma = Series(EoM.rolling(n).mean(), name = 'EOM' + str(n))
    df = df.join(Eom_ma)
    return df

# 顺势指标
def CCI(df, n):
    PP = (df['high'] + df['low'] + df['close']) / 3
    CCI = Series((PP - PP.rolling(n).mean()) / PP.rolling(n).std(), name = 'CCI' + str(n))
    df = df.join(CCI)
    return df

#估波指标
def COPP(df, n):
    M = df['close'].diff(int(n * 11 / 10) - 1)
    N = df['close'].shift(int(n * 11 / 10) - 1)
    ROC1 = M / N
    M = df['close'].diff(int(n * 14 / 10) - 1)
    N = df['close'].shift(int(n * 14 / 10) - 1)
    ROC2 = M / N
    Copp = Series((ROC1 + ROC2).ewm(span = n, min_periods = n).mean(), name = 'COPP' + str(n))
    df = df.join(Copp)
    return df

# 肯特纳通道
def KELCH(df, n):
    KelChM = Series(((df['high'] + df['low'] + df['close']) / 3).rolling(n).mean(),name = 'KelChM_' + str(n))
    KelChU = Series(((4 * df['high'] - 2 * df['low'] + df['close']) / 3).rolling(n).mean(), name = 'KelChU' + str(n))
    KelChD = Series(((-2 * df['high'] + 4 * df['low'] + df['close']) / 3).rolling(n).mean(), name = 'KelChD' + str(n))
    df = df.join(KelChM)
    df = df.join(KelChU)
    df = df.join(KelChD)
    return df

#终极振荡器
def ULTOSC(df):
    i = 0
    TR_l = [0]
    BP_l = [0]
    while i < df.index[-1]:
        TR = max(df._get_value(i + 1, 'high'), df._get_value(i, 'close')) - min(df._get_value(i + 1, 'low'), df._get_value(i, 'close'))
        TR_l.append(TR)
        BP = df._get_value(i + 1, 'close') - min(df._get_value(i + 1, 'low'), df._get_value(i, 'close'))
        BP_l.append(BP)
        i = i + 1
    UltO = Series((4 * Series(BP_l).rolling(7).sum()  / Series(TR_l).rolling(7).sum()) + (2 * Series(BP_l).rolling(14).sum() / Series(TR_l).rolling(14).sum()) + ( Series(BP_l).rolling(28).sum() /Series(TR_l).rolling(28).sum()), name = 'Ultimate_Osc')
    df = df.join(UltO)
    return df

# 唐奇安通道指标
def DONCH(df, n):
    i = 0
    DC_l = []
    while i < n - 1:
        DC_l.append(0)
        i = i + 1
    i = 0
    while i + n - 1 < df.index[-1]:
        DC = max(df['high'].ix[i:i + n - 1]) - min(df['low'].ix[i:i + n - 1])
        DC_l.append(DC)
        i = i + 1
    DonCh = Series(DC_l, name = 'Donchian' + str(n))
    DonCh = DonCh.shift(n - 1)
    df = df.join(DonCh)
    return df

# 计算最大回撤率和最大回撤幅度
def DDN(df):
    maxrate=((df['close'].cummax()-df['close'])/df['close'].cummax()).max()
    maxdown=(df['close'].cummax()-df['close']).max()
    return maxdown,maxrate
    
# 1.对价格序列取自然对数
# 2.对处理后的价格序列计算线性回归方程
# 3.将方程的斜率作为日收益，再计算其250次方获得年化收益
# 4.通过RSQ()函数计算判定系数（r-squared）
# 参考https://www.jianshu.com/p/1cf0dd67d9bd
def SCORE(df):
    y = df['log'] = np.log(df['close'])
    x = df['num'] = np.arange(df.log.size)
    slope, intercept = np.polyfit(x, y, 1)
    annualized_returns = pow(exp(slope), 250) - 1
    r_squared = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
    return annualized_returns * r_squared,annualized_returns
