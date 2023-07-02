from flask import Flask, jsonify
from flask_apscheduler import APScheduler

import json

import cfHunter
import datetime

# 创建 app
app = Flask(__name__)

# 创建定时器
scheduler = APScheduler()
scheduler.init_app(app=app)

contestInfos = [] # 比赛信息的列表，一个元素就是一天的查询结果

# 定时任务，每天早上执行一次，获取比赛信息
@scheduler.task("cron", id='GetContestInfo', day="*", hour="2", minute="0", second="0")
def GetContestInfo():
    todayContests = []
    todayContests.append(cfHunter.hunt())
    contestInfos.append({"time": datetime.datetime.now(), "data": todayContests})

@app.route("/", methods=["GET"])
def index():
    if len(contestInfos) == 0:
        GetContestInfo()
    print(contestInfos)
    return jsonify(contestInfos[-1])

if __name__ == "__main__":
    app.run(port=8000)