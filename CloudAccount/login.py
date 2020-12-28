from flask import current_app
from flask import request
from flask import render_template
from flask import redirect
from flask import session
from flask import jsonify
from flask import flash

from . import ca
from .models import makeMd5, sendMail, MysqlHelper
import random
import string
import time

# 登陆login login.html 
@ca.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # ---------------------------------------------------
        # 用户登陆验证代码块 开始
        # 成功则设置session for user,user_id
        phone = request.form.get('login_phone')
        pwd = request.form.get('login_pwd')
        db = MysqlHelper(config=current_app.config['DB_CONFIG'])
        sql = "SELECT `id`,`name`,`pwd`,`status` FROM `users` WHERE `phone`=%s LIMIT 1"
        val = (phone,)
        res = db.fetchone(sql, val)
        if not res: return jsonify('未知手机号，是否注册过？')
        elif not res[2]==makeMd5(pwd): return jsonify('密码错误')
        elif not res[3]: return jsonify('账号已禁用，请联系管理员')
        session['user_id'] = int(res[0])
        session['user'] = res[1]
        # 定义permanent为Ture，session的过期时间默认为31天
        if request.form.get('login_remember'): session.permanent = True
        else: session.permanent = False

        # ---------------------------------------------------
        # 默认门店验证代码块 开始
        # 成功则设置session for shop,shop_id
        db = MysqlHelper(config=current_app.config['DB_CONFIG'])
        sql = """SELECT `id`,`name`,`status` FROM `shops` 
        WHERE `id`=(SELECT shop_id FROM `authority` 
        WHERE `user_id`=%s AND `is_choice`=1 ORDER BY shop_id DESC LIMIT 1)"""
        val = (session['user_id'],)
        res = db.fetchone(sql, val)
        if not res:
            flash('%s，请切换到要操作的门店。' % (session['user']))
            return jsonify('2')
        elif not res[2]:
            flash('%s 已关停，请打开门店或联系门店创建人。' % (res[1]))
            return jsonify('2')
        session['shop_id'] = int(res[0])
        session['shop'] = res[1]
        flash('%s，欢迎你' % session['user'])
        return jsonify('1')

    # 如果不是POST
    else:
        return render_template('login.html')

# 注销用户logout 跳转login
@ca.route('/logout')
def logout():
    # 清除session中所有数据
    session.clear()
    return redirect('%s/login' % (current_app.config['APP_HOME']))

# 注册reg 跳转login(登陆页内操作)
@ca.route('/reg',methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        if current_app.config['DEBUG']:
            return jsonify('系统正在调试阶段，暂未开放注册。')
        # ---------------------------------------------------
        # 注册用户代码块 开始
        # 成功则设置session for user,user_id
        phone = request.form.get('reg_phone')
        pwd = request.form.get('reg_pwd')
        name = request.form.get('reg_name')
        mail = request.form.get('reg_mail')
        nowdate = time.strftime('%Y-%m-%d')
        # 查询手机号是否已注册
        db = MysqlHelper(config=current_app.config['DB_CONFIG'])
        sql = "SELECT COUNT(1) FROM `users` WHERE `phone`=%s;"
        val = (phone,)
        res = db.fetchone(sql, val)
        if res[0] != 0: return jsonify('手机号已注册，请更换或【找回密码】')
        # 写入数据到数据库
        db = MysqlHelper(config=current_app.config['DB_CONFIG'])
        sql = "INSERT INTO `users` (`phone`, `pwd`, `name`, `mail`, `reg_date`, `status`) VALUES (%s, %s, %s ,%s, %s, %s);"
        val = (phone, makeMd5(pwd), name, mail, str(nowdate), True)
        res = db.insert(sql, val)
        if int(res) == 0: return jsonify('注册失败，请联系管理员')
        session['user_id'] = int(res)
        session['user'] = name
        flash('%s，欢迎你！现在可以创建新门店。' % session['user'])
        return jsonify('2')
    else:
        return redirect('%s/login' % (current_app.config['APP_HOME']))

# 找回密码 跳转login(登陆页内操作)
@ca.route('/resetpwd',methods=['GET', 'POST'])
def resetpwd():
    if request.method == 'POST':
        # ---------------------------------------------------
        # 找回密码代码块 开始
        chk = request.form.get('resetpwd_chk',default='mail') #值：mail & phone
        text = request.form.get('resetpwd_text')
        # 是否匹配到手机号或邮箱地址 
        db = MysqlHelper(config=current_app.config['DB_CONFIG'])
        sql = "SELECT `id`,`status` FROM `users` WHERE `"+chk+"`=%s"
        val = (text,)
        res = db.fetchone(sql, val)
        if not res: return jsonify(('%s不存在' % (chk)).replace('phone','手机号').replace('mail','邮箱地址'))
        elif not res[1]: return jsonify('账号已禁用，请联系管理员')
        # 生成一个随机密码(8位数字)
        salt = ''.join(random.sample(string.digits, 8))
        # 发送邮件
        if chk == 'mail':
            mail_receiver = text
            mail_text = ('新密码：%s。【鹏辉记账】' % (salt))
        else:
            mail_receiver = 'wah@perfei.com'
            mail_text = ('手机号：%s，新密码：%s。【鹏辉记账】' % (text, salt))
        sendmail = sendMail(
            sender = current_app.config['MAIL_SENDER'],
            pwd = current_app.config['MAIL_PWD'],
            smtp = current_app.config['MAIL_SMTP'],
            port = current_app.config['MAIL_PORT'],
            receiver = mail_receiver,
            text = mail_text)
        if sendmail: 
            # 更新密码到数据库
            db = MysqlHelper(config=current_app.config['DB_CONFIG'])
            sql = "UPDATE `users` SET `pwd`=%s WHERE `id`=%s;"
            val = (makeMd5(salt), res[0])
            db.update(sql, val)
            return jsonify('1')
        else:
            return jsonify('邮件发送失败')
    else:
        return redirect('%s/login' % (current_app.config['APP_HOME']))

@ca.route('/manual')
def manual():
    return render_template("manual.html")
