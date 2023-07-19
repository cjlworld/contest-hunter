from flask_apscheduler import APScheduler
from . import contestInfos
from .contest_hunter import contestHunters
import datetime

from .. import scheduler

# 定时任务，每天早上执行一次，获取比赛信息
@scheduler.task("cron", id='GetContestInfo', day="*", hour="2", minute="0", second="0")
def GetContestInfo():
    todayContestsData = []
    for platform, hunter in contestHunters.items():
        todayContestsData.append(hunter.hunt())

    contestInfos.append({"time": datetime.datetime.now(), "data": todayContestsData})