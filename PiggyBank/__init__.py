#!/root/.pyenv/versions/pfbill_venv/bin/python
from flask import Blueprint, flash, jsonify, render_template, request

import mysql.connector
import random

# 定义蓝图
pb = Blueprint('pb', __name__, template_folder='')
# 定义数据库连接参数
DB_CONFIG = {
    'user': 'piggy_bank',
    'password': '5kvKv2EkO8Z4be2F',
    'database': 'piggy_bank',
    #'unix_socket': '/tmp/mysql.sock',
}

# 首页装饰器，必须带user参数
@pb.route('/')
@pb.route('/<user>', methods=['GET','POST'])
def index(user = None):
    # 定义数据库连接
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cur = db.cursor()
    except Exception as e:
        return ('<h1>连接异常: </h1><h2>{}</h2>'.format(e))

    # POST Ajax 请求
    if request.method == 'POST':
        # 获取前端form传递的数据
        details = request.form.get('details')
        income = float(request.form.get('income')) if request.form.get('income') else 0
        outgo = float(request.form.get('outgo')) * -1 if (request.form.get('outgo')) else 0

        # 存钱、花费操作块
        try:
            # 获取balance最新余额
            sql = '''SELECT `balance` FROM `tallies` 
                WHERE `user`=%s AND `acct_id`=%s ORDER BY `tly_time` DESC LIMIT 1;'''
            val = (user, 1)
            cur.execute(sql, val)
            balance = cur.fetchone()
            if balance:
                balance = float(balance[0]) + income + outgo
            else:
                balance = income + outgo
            # 添加新记录到 tallies
            sql = '''INSERT INTO `tallies` 
                (`details`, `income`, `outgo`, `balance`, `user`, `acct_id`) 
                VALUES (%s, %s, %s, %s, %s, %s);'''
            val = (details, income, outgo, balance, user, 1)
            cur.execute(sql, val)
            db.commit()
            flash('你记录了一笔[%s]！' % (details))
        except Exception as e:
            return jsonify(status = 0, message = '<p><b>数据库异常: </b></p><p>{}</p>'.format(e))
        finally:
            cur.close()
            db.close()
        # POST 请求完成，返回1
        return jsonify(status = 1)

    # GET 请求
    try:
        # 随机获取背景图
        bgimg = random.sample(['5'],1)[0] 
        # 获取用户表基本信息
        sql = '''SELECT `name`, `cash_balance`, `finance_balance`, `finance`, `rate`
            FROM `v_user` 
            WHERE `user`=%s;'''
        val = (user,)
        cur.execute(sql, val)
        res = cur.fetchone()
        if not res:
            raise Exception('The data of user [{}] does not exist.'.format(user))
        user_info = {
            'name':res[0],
            'cash_balance':res[1],
            'finance_balance': res[2],
            'finance': res[3],
            'rate': res[4],
            'bgimg': bgimg,
        }
        # 获取近3个月的记账数据
        sql = '''SELECT `month`, `day`, `time`, `details`, `amount` FROM `v_tly` 
            WHERE `tly_time`>=DATE_SUB(DATE_FORMAT(NOW(),'%Y-%m-1'), INTERVAL 2 MONTH) 
                AND `user`=%s AND `acct_id`=1 ;'''
        val = (user,)
        cur.execute(sql, val)
        res = cur.fetchall()
    except Exception as e:
        return ('<h1>系统错误：</h1><h2>{}</h2>'.format(e))
    finally:
        cur.close()
        db.close()
    #GET 请求完成，调用首页模板，返回html数据
    return render_template("index.html",
        user = user_info, tly = res)
