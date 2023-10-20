"""
    这是一个 app 包
"""

from flask import Flask

"""" 实例化扩展 """
from flask_apscheduler import APScheduler # as _BaseAPScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# """
#     封装 APScheduler, 给每个定时任务加上上下文
# """
# class APScheduler(_BaseAPScheduler):
#     def run_job(self, id, jobstore=None):
#         with self.app.app_context():
#             super().run_job(id=id, jobstore=jobstore)

"""
    A single-mode
"""
scheduler = APScheduler()
db = SQLAlchemy()
cors = CORS()

def create_app(config):
    """ 工厂函数 通过 config 构建一个 app 实例并返回 """
    app = Flask(__name__)

    """ 注册 BluePrint """
    from .api_bp import api_bp
    app.register_blueprint(api_bp, url_prefix="/")

    """ 获得 config, 之后可以把 config 变成 config.py"""

    for key in config:
        app.config[key] = config[key]

    """ 初始化扩展 """
    scheduler.init_app(app)
    # 别忘了 start
    scheduler.start()

    db.init_app(app)
    cors.init_app(app, resources=['/daily-report', '/contest-by-day'], origins=['*'])

    """ 初始化表 """
    with app.app_context():
        db.create_all()

    return app
