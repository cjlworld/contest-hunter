from flask import Flask, jsonify
from flask_apscheduler import APScheduler

import json

import contest_hunter
import datetime

# 创建 app
app = Flask(__name__)

# 创建定时器
scheduler = APScheduler()
scheduler.init_app(app=app)

contestInfos = [] # 比赛信息的列表，一个元素就是一天的查询结果

# 由爬取网站对象组成的字典（更新程序调用 hunt() 方法获取信息）
# 加入网站后在字典中加入相应的键值对
contestHunters = {
    "codeforces": contest_hunter.CodeforcesHunter(),
}

# 定时任务，每天早上执行一次，获取比赛信息
@scheduler.task("cron", id='GetContestInfo', day="*", hour="2", minute="0", second="0")
def GetContestInfo():
    todayContestsData = []
    for platform, hunter in contestHunters.items():
        todayContestsData.append(hunter.hunt())

    contestInfos.append({"time": datetime.datetime.now(), "data": todayContestsData})

@app.route("/", methods=["GET"])
def index():
    if len(contestInfos) == 0:
        GetContestInfo()
    print(contestInfos)
    return jsonify(contestInfos[-1])

if __name__ == "__main__":
    app.run(port=8000)