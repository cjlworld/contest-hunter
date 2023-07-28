from flask_restful import Resource
from flask import jsonify, request

from . import schedulers
from . import api
from .. import db
from ..models import Contest, DailyReportModel
from datetime import datetime, date
import json

"""
RESTful 接口

接口类继承 Resource, （命名为 ....Resource）
实现 

GET（SELECT）：从服务器取出资源（一项或多项）。
POST（CREATE）：在服务器新建一个资源。
PUT（UPDATE）：在服务器更新资源（客户端提供完整资源数据）。
PATCH（UPDATE）：在服务器更新资源（客户端提供需要修改的资源数据）。
DELETE（DELETE）：从服务器删除资源。
"""

@api.resource("/daily_report")
class DailyReportResource(Resource):
    """
        daily_report 接口，将日报视为资源
        GET         无参数，申请最新日报（不一定是当天的）
    """
    def get(self):
        schedulers.get_contest_info()
        # results = list(map(lambda x: x.serialize(), Contest.query.all()))
        # return jsonify(results)
        print(str(date.today()))
        result: DailyReportModel | None = DailyReportModel.query.filter_by(date=str(date.today())).first()
        if result is None:
            return {"status_code": "0", "data": None}
        return json.loads(result.jsons)

@api.resource("/contest_by_day")
class ContestByDayResource(Resource):
    """
        contest_by_day 接口，将每天的比赛信息视为资源
        GET             date = yyyy-mm-dd 
    """
    def get(self):
        request_json : dict | None = json.loads(request.data.decode("utf-8"))
        try: 
            request_date_str = str(request_json["date"])
            # 要把 format 写在后面
            # 真的是反人类的设计
            _ = datetime.strptime(request_date_str, "%Y-%m-%d")
        except Exception as err:
            print("Error: ", err)
            return {"status_code": "0", "data": None}
        
        result_contests: list[Contest] | None = Contest.query.filter_by(date=request_date_str).order_by(Contest.time).all()
        if result_contests is None:
            return {"status_code": "1", "data": None}
        result: list[dict] = [x.serialize() for x in result_contests]
        return {"status_code": "1", "data": result}

