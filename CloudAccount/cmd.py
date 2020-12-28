#!/root/.pyenv/versions/pfbill_venv/bin/python
import argparse
from typing import final
import mysql.connector
import random
import time

# 定义数据库连接字符串
db_config = {
    'user': 'cabook',
    'password': '7NyGXRLGPKZHBEct',
    'database': 'cabook',
    'unix_socket': '/tmp/mysql.sock',
}

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='tally AI.')
    parser.add_argument('-t', '--tally', help='tally AI.', action="store_true")
    args = parser.parse_args()
    if args.tally:
        tally()

def tally():
    """
    自动生成门店数据
    """
    db = mysql.connector.connect(**db_config)
    try:
        cur = db.cursor()

        # 定义sql语句及val参数列表
        sql = '''INSERT INTO `tallies`
            SELECT null, %s, %s, %s, `catg_id`, `acct_id` FROM `v_catg` 
            WHERE `catg_id`=%s AND `shop_id`=1;'''
        tly_day = int(time.strftime('%d'))
        old_month = 12 if int(time.strftime('%m'))-1==0 else int(time.strftime('%m'))-1
        tly_time = '%s:%d:00' % (time.strftime('%Y-%m-%d 20'), random.randrange(1,59))
        note = ''
        val = []
        # 收入：现金 2
        val.append((random.randrange(600,700), tly_time, None, 2))
        # 收入：微信 3
        val.append((random.randrange(2000,2300), tly_time, None, 3))
        # 收入：支付宝 43
        val.append((random.randrange(700,850), tly_time, None, 43))
        # 收入：意外来财 6
        if tly_day in [15, 30]:
            val.append((random.randrange(50,100), tly_time, '卖废品', 6))
        # 支出：伙食费 13
        val.append((random.randrange(50,60), tly_time, None, 13))
        # 支出：面粉 8
        if tly_day in [6, 16, 26]:
            val.append((1070, tly_time, '10包', 8))
        if tly_day % 4 ==0:
            # 支出：鸡蛋 9
            val.append((random.randrange(180,230), tly_time, '美菜1箱', 9))
        if tly_day % 3 == 0:
            # 支出：酸奶 10
            val.append((33.5, tly_time, '美菜1件', 10))
            # 支出：煤气 45
            val.append((190, tly_time, '两瓶', 45))
        if tly_day in [5, 15, 25]:
        # 支出：馅料款 11
            if tly_day == 5: note = '巴比%d月下' % (old_month)
            if tly_day == 15: note = '巴比%s月上' % ( time.strftime('%m') )
            if tly_day == 25: note = '巴比%s月中' % ( time.strftime('%m') )
            val.append((random.randrange(10000,13000), tly_time, note, 11))

        if tly_day == 10:
            # 支出：房租 15
            note = '%s月店租' % ( time.strftime('%m') )
            val.append((12450, tly_time, note, 15))
            # 支出：水电 16
            note = '%d月水电' % (old_month)
            val.append((random.randrange(800,950), tly_time, note, 16))
            # 支出：工资 17
            note = '%d月工资' % (old_month)
            val.append((13000, tly_time, note, 17))
        # executemany 批量写入数据库
        cur.executemany(sql, val)
        db.commit()
    except Exception as e:
        print('数据库异常: {}'.format(e))
    else:
        print('Cloud-account: 自动记账成功！')
        cur.close()
    finally:
        db.close()


if __name__ == '__main__':
    main()
