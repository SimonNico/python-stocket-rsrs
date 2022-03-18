import baostock as bs
import pandas as pd

def get_exchange_date():
    bs.login()
    rs = bs.query_trade_dates(start_date="2021-12-10")
    bs.logout()
    data_list = []
    while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    print(result)

if __name__=='__main__':
    get_exchange_date()
