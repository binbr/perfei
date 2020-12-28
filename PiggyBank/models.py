import mysql.connector

class Mysql:
    """Mysql数据库连接类

    属性:
        config:<dict> 数据库连接参数.

    方法：
        fetchone:<dict> 返回数据集的第一条记录
    """
    conn = None
    result = {} # 定义空字典

    def __init__(self, config={}):
        """初始化"""
        self.config = config

    def connect(self):
        """连接数据库"""
        self.conn = mysql.connector.connect(**self.config) # 初始化连接
        self.cursor = self.conn.cursor() # 初始化游标

    def close(self):
        """释放数据库"""
        self.cursor.close() # 释放游标
        self.conn.close() # 关闭连接

    def __exec(self, exec, sql, params):
        """执行SQL语句"""
        try:
            data = None
            self.connect()
            if exec == 'insertall':
                self.cursor.executemany(sql, params)
            else:
                self.cursor.execute(sql, params)
            if exec == 'fetchone':
                data = self.cursor.fetchone()
            elif exec == 'fetchall':
                data = self.cursor.fetchall()
            elif exec == 'insert':
                self.conn.commit()
                data = self.cursor.lastrowid
            elif exec in ['update', 'delete', 'insertall']:
                self.conn.commit()
                data = self.cursor.rowcount
            self.close()
            return {'status': 1,'data': data,}
        except Exception as e:
            return {'status': 0, 'error': e}

    def fetchone(self, sql, params=()):
        """返回数据集的第一条记录
        
        返回值<tupe>：返回一个元组，无数据返回None
        """
        if "SELECT" in str(sql).upper():
            return self.__exec('fetchone',sql,params)
        else:
            return {'status': 0,'error': ('Error:查询语句错误.')}

    def fetchall(self, sql, params=()):
        """返回一个数据集合
        
        返回值<list>：返回一个数据列表，无数据返回空[]
        """
        if "SELECT" in str(sql).upper():
            return self.__exec('fetchall',sql,params)
        else:
            return {'status': 0,'error': ('Error:查询语句错误.')}

    def insert(self, sql, params=()):
        """插入一条数据
        
        返回值<int>：返回插入的自增ID，无自增ID返回0
        """
        if "INSERT" in str(sql).upper():
            return self.__exec('insert',sql,params)
        else:
            return {'status': 0,'error': ('Error:插入语句错误.')}

    def insertall(self, sql, params=[]):
        """批量插入数据
        
        返回值<int>：返回插入条数，未插入返回-1
        """
        if "INSERT" in str(sql).upper():
            return self.__exec('insertall',sql,params)
        else:
            return {'status': 0,'error': ('Error:插入语句错误.')}

    def update(self, sql, params=()):
        """数据更新
        
        返回值<int>：返回更新的条数，无更新返回0
        """
        if "UPDATE" in str(sql).upper():
            return self.__exec('update',sql,params)
        else:
            return {'status': 0,'error': ('Error:更新语句错误.')}

    def delete(self, sql, params=()):
        """删除数据
        
        返回值<int>：返回删除的条数，无删除返回0
        """
        if "DELETE" in str(sql).upper():
            return self.__exec('delete',sql,params)
        else:
            return {'status': 0,'error': ('Error:删除语句错误.')}
