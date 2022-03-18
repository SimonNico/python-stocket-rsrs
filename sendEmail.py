from email import message
import pandas as pd
from sqlHelper import sqlHelper
import smtplib as sp
from email.mime.text import MIMEText

mai_host='smtp.163.com'
mail_user='jesselord'
mail_pw='sdfdsaeradghtrYUutw'
mail_sender='xxxxx@163.com'
receiver='<xxxx@foxmail.com>'
# receiver='<xxx@qq.com>'

def get_rsrs_data():
    sqlh=sqlHelper()
    sql="SELECT code 代码, code_name 名称, `date` 交易日期, prehigh 最高价, prelow 最低价, preclose 收盘价, M20, pre3M30 前三天M20最大值, scope 斜率, r2 拟合度, maxdval 最大回撤幅度, maxrate 最大回撤率, turn 换手率, amount 交易量, rsrs_suggest 建议, score 得分, annualized_returns 年化收益 FROM stocket.t_stock_rsrs where rsrs_suggest in ('建议买入','建议卖出') order by scope desc,r2 desc,score desc, maxrate"
    data,coldes=sqlh.get_data_withcol(sql)
    columnNames = [coldes[i][0] for i in range(len(coldes))]
    frame=pd.DataFrame(list(data),columns=columnNames)
    ht=frame.to_html(header=True,index=False)
    return ht

def send():
    html_str='''
    <html>
        <head><title></title>
        <style type="text/css">
            table {{ width: 1500px; min-height: 25px; line-height: 25px; text-align: center; border:1px solid #ccc; border-collapse: collapse;}}
        </style>
        </head>
        <body>
        <h3>说明:</h3>
        <h5>1、斜率大于0.7 且 M20大于前三天的M20 建议买入</h5>
        <h5>2、斜率小于-0.7  建议卖出</h5>
        <h5>3、拟合度越大说明拟合程度越好</h5>
        <h5>4、得分是基于年化收益率计算的 得分越高越好</h5>
        <h5>5、最大回撤率越低越好</h5>
        <font color=red siz=3>判断仅仅只做参考,不指导交易,请慎重考虑</font>
        <div>
        {table}
        </div>
        <body>
    </html>'''
    content=get_rsrs_data()
    msg=MIMEText(html_str.format(table=content),'html','utf-8')
    msg['From']=mail_sender
    msg['To']=receiver
    msg['Subject']='基于RSRS市场择时买卖信号提醒--沪深300'
    try:
        setpobj=sp.SMTP()
        setpobj.connect(mai_host,25)
        setpobj.login(mail_user,mail_pw)
        setpobj.sendmail(mail_sender,receiver,msg.as_string())
        print('success')
        setpobj.quit()
    except Exception as ex:
        print('error',ex)

if __name__=='__main__':
    send()
