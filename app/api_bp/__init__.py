from flask import Blueprint

contestInfos = [] # 比赛信息的列表，一个元素就是一天的查询结果

api_bp = Blueprint('api_blueprint', __name__)

from . import schedulers, views