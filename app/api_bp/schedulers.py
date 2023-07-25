from . import contest_hunter
import datetime
import json

from .. import scheduler
from .. import db
from ..models import Contest, DailyReportModel

def transform_dict_to_contest(contest_dict: dict):
    return Contest(
        title = contest_dict.get("title"), 
        length = contest_dict.get("length"), 
        time = contest_dict.get("time"), 
        rating = contest_dict.get("rating"), 
        platform = contest_dict.get("platform"), 
        date = contest_dict.get("time").split(" ")[0],
        update_time = "",
    )

# 定时任务，每天早上执行一次，获取比赛信息
@scheduler.task("cron", id='get_contest_info', day="*", hour="2", minute="0", second="0")
def get_contest_info():
    daily_report = contest_hunter.hunt_all()
    results = list(map(transform_dict_to_contest, daily_report))
    print(datetime.date.today())
    db.session.add(DailyReportModel(date=str(datetime.date.today()), jsons=json.dumps(daily_report)))

    for contest in results:
        if Contest.query.filter(Contest.title == contest.title, Contest.platform == contest.platform).first() is None:
            db.session.add(contest)
    
    db.session.commit()