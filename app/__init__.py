"""
    这是一个 app 包
"""

from flask import Flask
from flask_apscheduler import APScheduler
from flask_restful import Api

scheduler = APScheduler()
api = Api()

def create_app():
    """ 工厂函数 通过 config 构建一个 app 实例并返回 """
    app = Flask(__name__)

    """ 注册 BluePrint """
    from .api_bp import api_bp
    app.register_blueprint(api_bp)

    """ 初始化扩展 """
    scheduler.init_app(app)
    api.init_app(app)
    
    return app
