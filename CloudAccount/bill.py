from flask import current_app
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask import flash

from . import ca
from .models import MysqlHelper


# 查流水
@ca.route('/bill', methods=['GET','POST'])
def bill():
    db = MysqlHelper(config=current_app.config['DB_CONFIG'])
    # account POST请求
    if request.method == 'POST':
        pass

    # 无POST提交请求
    sql = '''SELECT month, day, time, 
            `catg_name`, `amount`, `acct_name`, `note`
        FROM `v_tly`
        WHERE `shop_id`=%s AND `tly_time`>=DATE_FORMAT(NOW(),'%Y-%m-1') AND `item_id` IN (1, 2);'''
    val = (session['shop_id'], )
    tly = db.fetchall(sql, val)
    return render_template("bill.html", tly = tly)

