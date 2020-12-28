from flask import current_app
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask import flash

from . import ca
from .models import MysqlHelper
import time

# 门店管理（已完成）
@ca.route('/shop', methods=['GET','POST'])
def shop():
    db = MysqlHelper(config=current_app.config['DB_CONFIG'])
    # shop POST请求
    if request.method == 'POST':
        # 获取表单数据，赋值 forms
        forms = request.form
        
        # change 切换门店操作
        if forms['exec_type'] == 'change':
            sql = """SELECT A.`is_choice`, S.`id`, S.`name`, S.`status` FROM `shops` AS S 
                INNER JOIN `authority` AS A ON S.`id`=A.`shop_id` 
                WHERE S.`id`=%s AND A.`user_id`=%s LIMIT 1"""
            val = (forms['id'], session['user_id'],)
            res = db.fetchone(sql, val)
            if not res: 
                return jsonify(status=0, message='门店信息有误，你无权管理此门店')
            elif not res[3]: 
                return jsonify(status=0, message='门店已停用，请先启用或联系门店创建人')
            # 成功则设置session for shop,shop_id
            session['shop_id'] = int(res[1])
            session['shop'] = res[2]
            # 更新数据库
            sql = "UPDATE `authority` SET `is_choice`=(CASE WHEN `shop_id`=%s THEN 1 ELSE 0 END) WHERE `user_id`=%s"
            val = (forms['id'], session['user_id'])
            db.update(sql, val)
            flash('已切换到[%s]' % (session['shop']))

        # gave 门店授权
        elif forms['exec_type'] == 'gave':
            return jsonify(status=0, message='你不能授权其他用户管理此门店<br>请联系管理员')

        # submit 创建/更新
        elif forms['exec_type'] == 'submit':
            if int(forms['id']) == 0:  #如果id=0 创建
                nowdate = time.strftime('%Y-%m-%d')
                sql = "INSERT INTO `shops`(`name`, `address`, `reg_date`, `status`) VALUES (%s, %s, %s ,%s);"
                val = (forms['name'], forms['addr'], str(nowdate), True)
                res = db.insert(sql, val)
                if res == 0: 
                    return jsonify(status=0, message='创建门店失败，请联系管理员')
                # 设置shop门店 session
                session['shop_id'] = int(res)
                session['shop'] = forms['name']

                sql = "INSERT INTO `authority`(`user_id`, `shop_id`, `is_admin`, `is_choice`) VALUES (%s,%s,%s,%s);"
                val = (session['user_id'], session['shop_id'], True, False)
                db.insert(sql, val)
                flash('%s 创建成功' % session['shop'])

            else:  # 更新
                # 验证当前用户是否对门店有操作权限
                sql = """SELECT S.`status` FROM `shops` AS S 
                    INNER JOIN `authority` AS A ON S.`id`=A.`shop_id` 
                    WHERE A.`user_id`=%s AND A.`shop_id`=%s AND A.`is_admin`=1"""
                val = (session['user_id'], forms['id'])
                res = db.fetchone(sql, val)
                if not res: 
                    return jsonify(status=0, message='你无权修改此门店资料')
                if not res[0]: 
                    return jsonify(status=0, message='门店已停用，请先启用或联系门店创建人')
                # 写入更新数据到数据库
                sql = "UPDATE `shops` SET `name`=%s,`address`=%s WHERE `id`=%s"
                val = (forms['name'], forms['addr'], forms['id'])
                db.update(sql, val)
                flash('门店资料修改成功')
        
        # 值=2时，前端刷新页面（通过flash传递信息）
        return jsonify(status = 2) 

    # 无POST请求
    else:
        # 列出当前账号名下所有门店
        sql = '''SELECT 
            `shop_id`,
            `name`,
            `address`,
            `status`,
            `is_admin`,
            `is_choice`
            FROM `v_shop` WHERE `user_id`=%s ORDER BY status DESC'''
        val = (session['user_id'],)
        res = db.fetchall(sql, val)
        return render_template("shop.html",
            res = res)

