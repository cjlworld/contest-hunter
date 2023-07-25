"""
    这是一个 app 包
"""

from flask import Flask

"""" 实例化扩展 """
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy

scheduler = APScheduler()
db = SQLAlchemy()

def create_app(config):
    """ 工厂函数 通过 config 构建一个 app 实例并返回 """
    app = Flask(__name__)

    """ 注册 BluePrint """
    from .api_bp import api_bp
    app.register_blueprint(api_bp, url_prefix = "/")

    """ 获得 config, 之后可以把 config 变成 config.py"""

    for key in config:
        app.config[key] = config[key]

    """ 初始化扩展 """
    scheduler.init_app(app)
    db.init_app(app)

    """ 初始化表 """
    from .models import Contest
    with app.app_context():
        db.drop_all()
        db.create_all()

    return app
