import pymysql
from pymysql.cursors import DictCursor
import traceback
import sys

class MysqlUti:
    def __init__(self):
        """初始化方法"""
        self.host = '127.0.0.1'
        self.user = 'root'
        self.password = 'root'
        self.database = 'notebook'
        self.connection = None
    def __enter__(self):
        self.connection = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database, cursorclass=DictCursor)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
    def insert(self, sql):
        """插入数据库"""
        #  PyBroadException
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except Exception as e: # 方法:捕获所有异常
            print("error", e)
        finally:
            if cursor:
                cursor.close()
    def fetchone(self, sql):
        """查询结果"""
        cursor = None
        result = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
        except:
            traceback.print_exc()
            self.connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if result:
                return result
    def fetchall(self, sql):
        """查询数据库多个结果集"""
        cursor = None
        results = []
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
        except:
            info = sys.exc_info()
            print(info[0],":", info[1])
            self.connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if results:
                return results
    def delete(self, sql):
        """删除结果集"""
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except:
            traceback.print_exc()
            self.connection.rollback()
        finally:
            if cursor:
                cursor.close()
    def update(self,sql):
        """更新结果集"""
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except:
            self.connection.rollback()
        finally:
            if cursor:
                cursor.close()

