import pymysql
from pymysql import cursors

class sqlHelper(object):
    def __init__(self) -> None:
        super().__init__()
        self.__conn_path={
            'host':'127.0.0.1',
            'user':'test',
            'password':'test123',
            'database':'stocket',
            'charset':'UTF8',
            'port':3306
        }
    
    def update_data(self,sql,arge=''):
        try:
            with pymysql.connect(**self.__conn_path) as conn:
                with conn.cursor() as cursor:
                    if isinstance(arge,list):
                        cursor.executemany(sql,arge)
                        conn.commit()
                    else:
                        cursor.execute(sql,arge)
                        conn.commit()    
            return 1
        except Exception as ex:
            print("-----更新操作失败",ex)
            return -1

    def get_data(self,sql,arge=tuple()):
        try:
            if not isinstance(arge,tuple):
                raise Exception("arge 参数类型错误")
            with pymysql.connect(**self.__conn_path) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql,arge)
                    return cursor.fetchall()
        except Exception as ex:
            print("-----查询失败",ex)
            return None
    
    def get_data_withcol(self,sql,arge=tuple()):
        try:
            if not isinstance(arge,tuple):
                raise Exception("arge 参数类型错误")
            with pymysql.connect(**self.__conn_path) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql,arge)
                    return cursor.fetchall(),cursor.description
        except Exception as ex:
            print("-----查询失败",ex)
            return None


