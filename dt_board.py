# -*- coding: utf-8 -*-
# 实现， 东方财富的 龙虎榜爬虫 
import pandas as pd
import numpy as np
from scrapy import Selector
import urllib
import urllib.request
import urllib.error
import datetime, time
import re


def dateRange(start, end, step=1, format="%Y-%m-%d"):
    strptime, strftime = datetime.datetime.strptime, datetime.datetime.strftime
    days = (strptime(end, format) - strptime(start, format)).days 
    return [strftime(strptime(start, format) + datetime.timedelta(i), format) for i in range(0, days +1 , step)]
    
def Get_LHB_stocks_from_excel(begin_date, end_date):
    Timeline = dateRange(begin_date, end_date)
    dfs = pd.DataFrame()
    for date_id in Timeline:
#        print( 'Date: ', date_id )
        URL_stocks_infos = r'http://data.eastmoney.com/DataCenter_V3/stock2016/TradeDetail/pagesize=200,page=1,sortRule=-1,sortType=,startDate='+ date_id + ',endDate=' +  date_id + ',gpfw=0,js=var%20data_tab_1.html?rt=26442172'
        html = urllib.request.urlopen(URL_stocks_infos).read()
        html = html.decode('gb2312','ignore')
        X = re.split( ',"url"' , html )[0]
        X = re.split( '"data":' , X )[1]        
        df = pd.read_json( X , orient='records')
        if(len(df) != 0 ):
            df2 = df[['Tdate', 'SCode', 'SName','JD','ClosePrice', 'Chgradio', 'JmMoney', 'Bmoney', \
                     'Smoney', 'ZeMoney', 'Turnover', 'JmRate', 'ZeRate', 'Dchratio', 'Ltsz', 'Ctypedes' ]]
            colunms_name = ['Code', 'Name', '解读', '收盘价', '涨跌幅', '龙虎榜净买额', '龙虎榜买入额', '龙虎榜卖出额', \
                            '龙虎榜成交额', '市场总成交额', '净买额占总成交比', '成交额占比' , '换手率', '流通市值', '上榜原因']
            df2 = df2.rename( columns = {'Tdate': 'Date', 'SCode': colunms_name[0], 'SName':colunms_name[1], 'JD': colunms_name[2], 'ClosePrice': colunms_name[3] , \
                                         'Chgradio': colunms_name[4], 'JmMoney': colunms_name[5], 'Bmoney': colunms_name[6], \
                     'Smoney':colunms_name[7], 'ZeMoney':colunms_name[8], 'Turnover':colunms_name[9], 'JmRate':colunms_name[10], \
                     'ZeRate':colunms_name[11], 'Dchratio':colunms_name[12], 'Ltsz':colunms_name[13], 'Ctypedes':colunms_name[14] } )
            df2['Wind_Code'] = str( df2['Code'] )
            S_codes = list() 
            for i in df2['Code']:
                if( len( str(i) ) <6 ):
                    s = '0'*(6-len( str(i) )) + str(i)
                else:
                    s = str(i)
                if(s[0] == '6'):
                    s = s+'.SH'
                else:
                    s = s+'.SZ'
                if( len(S_codes) ==0 ):
                    S_codes = [s]
                else:
                    S_codes.append(s)
            df2['Wind_Code'] = S_codes
            print( 'Date: ', date_id, '上榜条数: ', len(df2), ',  上榜股票只数: ', len( df2['Wind_Code'].unique() ) )
            dfs = dfs.append(df2)
        else:
            print( 'Date: ', date_id, '上榜条数: ', 0, ',  上榜股票只数: ', 0 )
    return dfs

def Crawl_web(code, date):
    url = 'http://data.eastmoney.com/stock/lhb,'+ date +','+ code[0:6] +'.html'
    ########
    content = urllib.request.urlopen(url).read()
    content = content.decode('gb2312','ignore')
    sel = Selector(text = content).xpath('//div[@class="data-tips"]//div[@class="left con-br"]//text()').extract()
    Table_datas = pd.DataFrame()
    for i in range(len(sel)):
        s_type = sel[i].split('类型：')[1]
        data1 = Selector(text = content).xpath('//div[@class="data-tips"]//div[@class="right"]//span//text()').extract()
        P_close = data1[0]
        Rtn = data1[1]
    ###################
        links_table_buy = Selector(text = content).xpath('//div[@class="content-sepe"]//table[@class="default_tab stock-detail-tab"]//tbody')
        links_table_sell = Selector(text = content).xpath('//div[@class="content-sepe"]//table[@class="default_tab tab-2"]//tbody')
        ####################
        List_buy_top, Table_data_buy = HTML_Parse( [links_table_buy[i]] )
        Table_data_buy['ID'] = 'top_buy'
        List_sell_top, Table_data_sell = HTML_Parse( [links_table_sell[i]] )
        Table_data_sell['ID'] = 'top_sell'
        Table_data = pd.concat( [Table_data_buy, Table_data_sell], ignore_index=True)
        Table_data['Code'] = code
        Table_data['Date'] = date
        Table_data['Type'] = s_type
        Table_data['P_close'] = P_close
        Table_data['Rtn'] = Rtn
        Table_datas = Table_datas.append(Table_data)
    if(len(Table_datas)>0):
        Table_datas = Table_datas[['Code', 'Date', 'Type', 'P_close', 'Rtn', 'ID', 'sec_name', 'amt_buy', 'amt_sell' ]]
    return Table_datas 

def HTML_Parse(links_tables):
    List = [] 
    for ind, link_table in enumerate(links_tables):
        links = link_table.xpath('.//tr')        
        for ind2, link2 in enumerate(links):
            sc_name = link2.xpath('.//td//div[@class="sc-name"]//a//text()').extract()
            if( len(sc_name) >0):
                Amt_buy = link2.xpath('.//td[@style="color:red"]//text()').extract()
                Amt_sell = link2.xpath('.//td[@style="color:Green"]//text()').extract()
                if(len(Amt_buy)>0):
                    Amt_buy = Amt_buy[0]
                else:
                    Amt_buy = np.nan
                if(len(Amt_sell)>0):
                    Amt_sell = Amt_sell[0]
                else:
                    Amt_sell = np.nan            
#                print(sc_name, Amt_buy, Amt_sell)
                List.append([sc_name[0], Amt_buy, Amt_sell])
    table_data = pd.DataFrame(List)
    table_data = table_data.rename(columns = {0:'sec_name', 1:'amt_buy', 2:'amt_sell'})
    return List, table_data

def main(begin_date, end_date):
    Stocks_info = Get_LHB_stocks_from_excel(begin_date, end_date)
    Timeline_unique = np.unique(Stocks_info['Date']) 
    for date in Timeline_unique:
        Table_datas = pd.DataFrame()  
        CODES = Stocks_info[Stocks_info['Date'] == date]['Wind_Code'].unique()
        for code in CODES: 
            df = [] 
            print('Downloading ......', code, date)
            df = Crawl_web(code, date) 
            repeat_times = 1 
            while(len(df) == 0 and repeat_times <= 10 ):
                print('...... length 为 0 ...... ', code, date)
                time.sleep(60*3)
                df = Crawl_web(code, date) 
                if(len(df)>0):
                    print('Sucessful Download ......', code, date)
                repeat_times = repeat_times + 1
            Table_datas = Table_datas.append(df)        
        str_result_filename = "./data/龙虎榜具体信息_"+ str( min(Table_datas['Date'])) + '_'+ str( max(Table_datas['Date'])) + ".xlsx"
        writer = pd.ExcelWriter(str_result_filename) 
        Table_datas.to_excel(writer, sheet_name = 'LHB' , index=False)  
        writer.save()  
    ##########################
    str_result_filename = "./龙虎榜综合信息_"+ str( min(Stocks_info['Date'])) + '_'+ str( max(Stocks_info['Date'])) + ".xlsx"
    writer = pd.ExcelWriter(str_result_filename) 
    Stocks_info.to_excel(writer, sheet_name = '龙虎榜日综合数据' , index=False)  
    writer.save()
    return 0 
    
########### main function ########################      
if __name__ == '__main__': 
    begin_date = '2021-12-13' 
    end_date = '2021-12-13' 
#    Stocks_info = Get_LHB_stocks_from_excel(begin_date, end_date) 
    main(begin_date, end_date)    



