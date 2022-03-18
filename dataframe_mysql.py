from pandas.core import indexing
from sqlalchemy import create_engine
import pandas as pd
from urllib.parse import quote_plus as urlquate

user='test'
passwd='test123'
dbhost='127.0.0.1'
dbport=3306
dbname='stocket'
db_cnn=f'mysql+pymysql://{user}:{urlquate(passwd)}@{dbhost}:{dbport}/{dbname}'

def insert_600_data(df):
    conn=create_engine(db_cnn)
    df.to_sql('t_stock_600data',conn,if_exists='append',index=False)

def insert_hs300_list(df):
    conn=create_engine(db_cnn)
    df.to_sql('t_stock_hs300list',conn,if_exists='append',index=False)