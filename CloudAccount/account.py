from flask import current_app
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask import flash

from . import ca
from .models import MysqlHelper

#资金账户（已完成）
@ca.route('/account', methods=['GET','POST'])
def account():
    db = MysqlHelper(config=current_app.config['DB_CONFIG'])
    # account POST请求
    if request.method == 'POST':
        # 获取表单数据，赋值 forms
        forms = request.form
        
        # submit 创建/更新
        if forms['exec_type'] == 'submit':
            if int(forms['id']) == 0:  #创建
                sql = "INSERT INTO `accounts`(`name`, `shop_id`) VALUES (%s, %s);"
                val = (forms['name'], session['shop_id'])
                res = db.insert(sql, val)
                if res == 0: return jsonify(status=0, message='创建失败，请联系管理员')
                flash('[%s] 添加成功！' % (forms['name']))
            else:  #更新
                sql = "UPDATE `accounts` SET `name`=%s WHERE `id`=%s AND `shop_id`=%s;"
                val = (forms['name'], forms['id'], session['shop_id'])
                res = db.update(sql, val)
                if res == 0: return jsonify(status=0, message='更新失败，你没有修改权限')
                flash('[%s] 修改成功！' % (forms['name']))
            return jsonify(status = 2) #值=2时，前端刷新页面（通过flash传递信息）
        # del 删除
        elif forms['exec_type'] == 'del':
            return jsonify(status=0, message='账户已关联项目，请先解除关联')

    # 无POST提交请求
    else:
        sql = "SELECT `id`, `name`, `amount` FROM `accounts` WHERE `shop_id`=%s;"
        val = (session['shop_id'],)
        res = db.fetchall(sql, val)
        return render_template("account.html",
            res = res)
