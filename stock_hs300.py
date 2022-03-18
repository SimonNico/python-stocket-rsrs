import pandas as pd
import baostock as bs
from dataframe_mysql import insert_hs300_list

def get_hs300_data():
    bs.login()
    rs = bs.query_hs300_stocks()
    bs.logout()
    hs300_stocks = []
    while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
        hs300_stocks.append(rs.get_row_data())
    result = pd.DataFrame(hs300_stocks, columns=rs.fields)
    return result

if __name__=='__main__':
    df=get_hs300_data()
    insert_hs300_list(df)