#!/root/.pyenv/versions/perfei_env/bin/python
from flask import Flask
from flask import redirect

# 引用蓝图
from CloudAccount import ca
from PiggyBank import pb

app = Flask(__name__)
app.config.from_object('config')

# 注册蓝图
app.register_blueprint(ca, subdomain='ca')
app.register_blueprint(pb, subdomain='pb')

@app.route('/')
def index():
    return redirect('https://www.perfei.com/')


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=int(app.config['PORT']), debug=app.config['DEBUG'])
