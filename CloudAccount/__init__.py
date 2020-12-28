from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import request
from flask import session
from flask import flash

from .models import MysqlHelper
import time

ca = Blueprint('ca', __name__, template_folder='templates')

from . import account     # 资金账户
from . import bill        # 查账
from . import category    # 分类管理
from . import login       # 登陆、注册、注销
from . import report      # 报表
from . import shop        # 门店管理
from . import tally       # 记账

# /---------------------------------------------------
# 在每一次请求进入视图函数之前做出响应
# 判断是否登陆，以及是否选择操作门店
@ca.before_request
def before_request():
    # 排除项
    if request.path in ["/login", "/shop", "/logout", '/reg', '/resetpwd', '/manual']: 
        return None
    # 未登陆，跳转到login页面
    if not session.get('user_id'):
        return redirect('%s/login' % (current_app.config['APP_HOME']))
    # 已登陆且有操作门店，验证权限
    if session.get('shop_id'):
        db = MysqlHelper(config=current_app.config['DB_CONFIG'])
        # 读取v_shop视图表数据集
        sql = '''SELECT COUNT(0) FROM `v_shop` WHERE `user_id`=%s AND `shop_id`=%s AND `status`=1;'''
        val = (session['user_id'], session['shop_id'],)
        if db.fetchone(sql, val)[0] == 0:
            session.pop('shop_id')
            session.pop('shop')
    # 已登陆但无操作门店或验证权限未通过，跳转到shop页面
    if not session.get('shop_id'):
        flash('%s，请切换到要操作的门店。' % (session['user']))
        return redirect('%s/shop' % (current_app.config['APP_HOME']))
    return None
# ---------------------------------------------------/

# /---------------------------------------------------
# get() 全局函数，可以直接在jinja2模板中调用
# key:      参数：要获取的键
# value:    参数：要获取的值
# result:   返回值
@ca.app_template_global()
def get(key = '', value = None):
    result = None
    # 获取 session 值
    if key == 'session':
        result = session.get(value)
    # 获取 item 数据集
    elif key == 'item':
        db = MysqlHelper(config=current_app.config['DB_CONFIG'])
        # 读取items表数据集
        sql = '''SELECT `id`, `name`, `is_inacct` FROM `items`;'''
        result = db.fetchall(sql)
    # 获取 item 数据集
    elif key == 'acct':
        db = MysqlHelper(config=current_app.config['DB_CONFIG'])
        # 读取accounts表数据集
        sql = '''SELECT `id`, `name` FROM `accounts` WHERE `shop_id`=%s;'''
        val = (session['shop_id'],)
        result = db.fetchall(sql, val)
    # 获取当前时间，并格式化
    elif key == 'now':
        result = time.strftime('%Y-%m-%dT%H:%M:%S')
    # 获取 tally 数据集
    elif key == 'tly':
        pass
    return result
# ---------------------------------------------------/

# /---------------------------------------------------
# 过滤器函数，template_filter(),也是全局的，不需要传值，模板中直接用即可
# 未使用，保留
#
#
#@ac.template_filter()
#def filter(a, b, c):    
#    print(a)
#    return a + b + c
# ---------------------------------------------------/
