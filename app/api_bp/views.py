from flask_restful import Resource
from flask import jsonify

from . import contestInfos
from . import schedulers
from .. import api

@api.resource("/")
class DailyReport(Resource):
    def get(self):
        if len(contestInfos) == 0:
            schedulers.GetContestInfo()
        # print(contestInfos)
        return jsonify(contestInfos[-1])