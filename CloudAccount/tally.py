from flask import current_app
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask import flash

from . import ca
from .models import MysqlHelper

# tally 记账
@ca.route('/', methods=['GET','POST'])
def tally():
    db = MysqlHelper(config=current_app.config['DB_CONFIG'])
    # account POST请求
    if request.method == 'POST':
        # 获取表单数据，赋值 forms
        forms = request.form
        # 将获取到的表单数据添加到元组列表
        val = []
        if forms.get('item_id') in ['1','2'] and forms.get('amount'):
            # 配置SQL语句数组
            val.append((
                forms.get('amount'), 
                forms.get('nowdate'), 
                forms.get('note'), 
                forms.get('acct_id'), 
                forms.get('catg_id'), 
                session['shop_id'],
                ))
        else:
            for k,v in forms.items():
                if ('amount' in k and v != ''):
                    # 配置SQL语句数组
                    val.append((
                        v, 
                        forms['nowdate'], 
                        None,
                        forms.get('acct_id'+k.split(':',2)[1]),
                        k.split(':',2)[1], 
                        session['shop_id'],
                        ))
        if len(val) < 1:
            return jsonify(status=0, message='没有需要提交的数据。')
        # 定义添加记录的SQL语句
        sql = '''INSERT INTO `tallies`
            SELECT %s, %s, %s, `catg_id`, %s FROM `v_catg` 
            WHERE `catg_id`=%s AND `shop_id`=%s;'''
        res = db.insertall(sql, val)
        # 添加数据成功返回添加的数据条数
        if not res :
            return jsonify(status=0, message='提交数据失败，请联系管理员')
        flash('成功添加[ %d ]条记账！' % (res))
        return jsonify(status=2)

    # 无POST提交请求
    else:
        # 获取GET参数
        item_id = int(request.args.get('item_id')) if request.args.get('item_id') else 0
        sql = '''SELECT 
            `catg_id`, 
            `pid`, 
            `name`, 
            `is_homepage`,
            `is_inacct`,
            `acct_id`, 
            `item_id`
            FROM `v_catg` WHERE `shop_id`=%s AND '''
        # 读取分类表
        if item_id == 0:
            sql = sql + '`is_homepage`=1 ;'
            val = (session['shop_id'], )
        else:
            sql = sql + '`item_id`=%s ;'
            val = (session['shop_id'], item_id, )
        #return jsonify(status=1,message=sql)
        res = db.fetchall(sql, val)
        sql = '''SELECT day, 
                time, 
                `catg_name`, 
                `amount`, 
                `acct_name`, 
                `note` 
            FROM `v_tly`
            WHERE `tly_time`>=DATE_FORMAT(NOW(),'%Y-%m-%d') AND `shop_id`=%s AND `item_id`=%s;'''
        val = (session['shop_id'], item_id, )
        tly = db.fetchall(sql, val)
        return render_template("tally.html", res = res, tly = tly)
