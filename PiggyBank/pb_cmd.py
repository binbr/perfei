#!/root/.pyenv/versions/perfei_env/bin/python
import mysql.connector
import argparse

# 定义数据库连接字符串
db_config = {
    'unix_socket': '/tmp/mysql.sock',
    'user': 'piggy_bank',
    'password': '5kvKv2EkO8Z4be2F',
    'database': 'piggy_bank',
}
db = mysql.connector.connect(**db_config)

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='Piggy-Bank Financial management procedures.')
    parser.add_argument('-u', '--user', type=str, help="The user name to operate on. eg:-u yourname")
    parser.add_argument('-a', '--add', type=int, help='Deposit into financial account. eg:-a 100')
    parser.add_argument('-o', '--out', type=int, help='Withdraw from financial account. eg:-o 100')
    parser.add_argument('-g', '--gain', action="store_true", help='Calculate the daily gains of financial account.')
    args = parser.parse_args()

    if (args.user and args.add) or (args.user and args.out):
        if args.add:  # 参数为 add
            tally('存入', args.user, args.add)
        if args.out:  # 参数为 out
            tally('取出', args.user, args.out)
    elif args.gain:
        tally('收益')  # 参数为 gain
    else:
        print('需要同时指定用户参数及存入或取出的金额数'
            '\n例：-u yourname -a 200'
            '\n或：-u yourname -o 100')
    db.close()  # 关闭数据库连接


def tally(details, user=None, amount=0):
    """
    记账函数。
    参数： details: 摘要, user: 用户名, amount: 金额
    """
    try:
        cur = db.cursor()
        # 获取用户信息表
        sql = 'SELECT `user`, `finance_balance`, `finance`, `rate` FROM `v_user` WHERE '
        if user:
            if details == '取出':
                sql +='`finance`>=%d AND ' % amount
            if details == '存入':
                sql +='`finance`<=10000-%d AND ' % amount
            sql += '`user`="%s";' % user
        else:
            sql += '`finance`>0;'
        cur.execute(sql)
        users = cur.fetchall()
        if not users:
            raise Exception('用户不存在或金额超出限额')

        # 定义sql语句及val参数列表
        sql = '''INSERT INTO `tallies` 
            (`details`, `income`, `outgo`, `balance`, `user`, `acct_id`) 
            VALUES (%s, %s, %s, %s, %s, 2);'''
        val = []
        for u in users:
            # 根据details定义income或outgo的值
            income = outgo = 0
            if details == '收益':
                income = float(u[2]*u[3])
            elif details == '存入':
                income = float(amount)
            elif details == '取出':
                outgo = float(amount * -1)
            val.append((details, income, outgo, float(u[1])+income+outgo, u[0]))
            if user:
                # 更新用户表的数据
                cur.execute(
                    'UPDATE `users` SET `finance`=`finance`+%s WHERE `user`=%s;',
                    (income+outgo, user))
        cur.executemany(sql, val)  # executemany 批量写入数据库
        db.commit()
    except mysql.connector.Error as e:
        db.rollback()
        print('数据库异常: {}'.format(e))
    except Exception as e:
        print('错误：{}'.format(e))
    else:
        print('Piggy-bank: 添加了{}笔！'.format(cur.rowcount))
        cur.close()  # 关闭游标

if __name__ == '__main__':
    main()

