from flask import current_app
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask import flash

from . import ca
from .models import MysqlHelper


# 统计报表
@ca.route('/report', methods=['GET','POST'])
def report():
    return render_template("report.html",
        )

