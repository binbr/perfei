from datetime import *
import mysql.connector
import hashlib
import time
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

#定义数据库连接类
class MysqlHelper:
    #定义空连接
    conn = None

    #初始化变量及类
    def __init__(self, config={}):
        self.config = config

    #连接数据库
    def connect(self):
        try:
            #初始化数据库连接 mysql.connector.connect
            self.conn = mysql.connector.connect(**self.config)
            #初始化数据库游标
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as e:
            print('数据库connect异常: {}'.format(e))

    #释放数据库
    def close(self):
        #释放数据游标
        self.cursor.close()
        #关闭数据库
        self.conn.close()

    # 获取数据库返回集中第一条记录(改造完成)
    # sql:      参数：sql查询语句
    # params:   参数：参数值的列表
    # return:   返回值：成功返回一条数据，失败返回None
    def fetchone(self, sql, params=()):
        #定义空数据集
        result = None
        try:
            if "SELECT" in str(sql).upper():        #检测是否为查询语句
                self.connect()                      #连接数据库
                self.cursor.execute(sql, params)    #执行查询命令
                result = self.cursor.fetchone()     #返回第一条记录
        except mysql.connector.Error as e:
            print('数据库查询异常: {}'.format(e))
        finally:
            self.close()
        return result

    # 获取数据库返回全部数据集合(改造完成)
    # sql:      参数：sql查询语句
    # params:   参数：参数值的列表
    # return:   返回值：成功返回数据集合，失败返回None
    def fetchall(self, sql, params=()):
        #定义数据列表集合
        list_data = ()
        try:
            if "SELECT" in str(sql).upper():        #检测是否为查询语句
                self.connect()                      #连接数据库
                self.cursor.execute(sql, params)    #执行查询命令
                list_data = self.cursor.fetchall()  #返回全部记录
        except mysql.connector.Error as e:
            print('数据库查询异常: {}'.format(e))
            return None
        finally:
            self.close()
        return list_data

    # 执行插入语句(改造完成)
    # sql:      参数：sql查询语句
    # params:   参数：参数值的列表
    # return:   返回：成功返回插入的id，失败返回None
    def insert(self, sql, params=()):
        lastrowid = 0
        try:
            self.connect()                              #连接数据库
            self.cursor.execute(sql, params)            #执行数据库命令语句
            self.conn.commit()                          #把命令推送到服务器
            lastrowid = self.cursor.lastrowid           #返回插入的自增ID
        except mysql.connector.Error as e:
            print('数据库插入异常: {}'.format(e))
            return None
        finally:
            self.close()
        return lastrowid                                    #返回插入的自增ID

    # 执行批量插入语句(改造完成)
    # sql:      参数：sql查询语句
    # params:   参数：参数值的列表
    # return:   返回：成功返回插入的条数，失败返回None
    def insertall(self, sql, params=[]):
        try:
            self.connect()                              #连接数据库
            self.cursor.executemany(sql, params)            #执行数据库命令语句
            self.conn.commit()                          #把命令推送到服务器
        except mysql.connector.Error as e:
            print('数据库批量插入异常: {}'.format(e))
            return None
        finally:
            self.close()
        return len(params)

    #执行数据库更新
    def update(self, sql, params=()):
        if "UPDATE" in str(sql).upper():        #检测是否为更新语句
            return self.__edit(sql, params)
        else:
            return None

    #执行数据删除
    def delete(self, sql, params=()):
        if "DELETE" in str(sql).upper():        #检测是否为删除语句
            return self.__edit(sql, params)
        else:
            return None

    #执行其他特殊命令 慎用
    def cmdsql(self, sql, params=()):
        return self.__edit(sql, params)

    #执行命令函数
    def __edit(self, sql, params):
        #定义影响行数
        count = 0
        try:
            self.connect()                              #连接数据库
            count = self.cursor.execute(sql, params)    #执行数据库命令语句
            self.conn.commit()                          #把命令推送到服务器
            self.close()
        except Exception as e:
            print(e)
        return count                                    #返回受影响的行数
  #db = MysqlHelper(config=app.config['DB_CONFIG'])
  #sql = "SELECT `id`,`name`,`pwd`,`status` FROM `users` WHERE `phone`=%s LIMIT 1"
  #val = (phone,)
  #res = db.fetchone(sql, val)
  #del db

# 生成md5
def makeMd5(mstr):
    hmd5 = hashlib.sha256(bytes('a0c3!a5#4f48',encoding="utf-8"))
    hmd5.update(bytes(mstr,encoding="utf-8"))
    return hmd5.hexdigest()
# 获取unix时间戳
def getTime():
    return round(time.time())
# 时间格式化
def timeFormat(timestamp):
    #return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    #return datetime.fromtimestamp(timestamp)
    return datetime.utcfromtimestamp(timestamp)

# 邮件发送函数
# sender 发件人邮箱账号
# pwd 发件人邮箱密码
# receiver 收件人邮箱账号，我这边发送给自己
# text 邮件正文内容
def sendMail(sender,pwd,smtp,port,receiver,text):
    ret=True
    try:
        msg=MIMEText(text,'plain','utf-8')
        msg['From']=formataddr(["鹏辉记账",sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        #msg['To']=formataddr(["收件人邮箱昵称",receiver])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['To']=''.join(receiver)
        msg['Subject']="鹏辉记账-密码重置邮件"                # 邮件的主题，也可以说是标题
 
        server=smtplib.SMTP_SSL(smtp, int(port))  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(sender, pwd)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(sender,receiver,msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()
    except Exception:
        ret=False
    return ret
    #ret=sendMail(str,str,str,str)
    #if ret:
    #    print("邮件发送成功")
    #else:
    #    print("邮件发送失败")
