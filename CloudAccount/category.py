from flask import current_app
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask import flash

from . import ca
from .models import MysqlHelper


# 分类管理（已完成）
@ca.route('/category', methods=['GET','POST'])
def category():
    db = MysqlHelper(config=current_app.config['DB_CONFIG'])
    # category POST请求
    if request.method == 'POST':
        # 获取表单数据，赋值 forms
        forms = request.form

        # submit 创建/更新
        if forms['exec_type'] == 'submit':
            if int(forms['id']) == 0:  #如果id=0 创建
                sql = """INSERT INTO `categories` 
                    (`pid`, `name`, `item_id`, `account_id`, `shop_id`, `is_homepage`) 
                    VALUES (%s, %s, %s, %s, %s, %s);"""
                val = (forms['pid'], forms['name'], forms['item_id'], 
                    forms.get('account_id'), session['shop_id'], 
                    True if forms.get('is_homepage') else False)
                res = db.insert(sql, val)
                if res == 0: 
                    return jsonify(status=0, message='创建失败，请联系管理员')
                flash('[%s] 添加成功！' % (forms['name']))
            else:  #否则 更新
                sql = "UPDATE `categories` SET `name`=%s, `pid`=%s, `account_id`=%s, `is_homepage`=%s WHERE `id`=%s AND `shop_id`=%s;"
                val = (forms['name'], forms['pid'], forms.get('account_id'), True if forms.get('is_homepage') else False, forms['id'], session['shop_id'])
                res = db.update(sql, val)
                if res == 0: 
                    return jsonify(status=0, message='更新失败，你没有修改权限')
                flash('[%s] 修改成功！' % (forms['name']))

        # del 删除
        elif forms['exec_type'] == 'del':
            return jsonify(status=0, message='分类已关联项目，请先解除关联')

        # 值=2时，前端刷新页面（通过flash传递信息）
        return jsonify(status = 2) 

    # 无POST请求
    else:
        # 获取GET参数
        item_id = int(request.args.get('item_id')) if request.args.get('item_id') else 1
        # 读取分类表
        sql = '''SELECT 
            `catg_id`, 
            `pid`, 
            `name`, 
            `is_inacct`,
            `is_homepage`, 
            `acct_id` 
            FROM `v_catg` 
            WHERE `shop_id`=%s AND `item_id`=%s; '''
        val = (session['shop_id'], item_id,)
        res = db.fetchall(sql, val)
        return render_template("category.html",
            res = res,
            )
