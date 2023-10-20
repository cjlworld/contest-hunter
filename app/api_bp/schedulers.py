from . import contest_hunter
import datetime
import json

from .. import scheduler
from .. import db
from ..models import Contest, DailyReportModel

def transform_dict_to_contest(contest_dict: dict):
    time_str: str = str(contest_dict.get("time"))
    return Contest(
        title = contest_dict.get("title"), 
        length = contest_dict.get("length"), 
        time = time_str,
        rating = contest_dict.get("rating"), 
        platform = contest_dict.get("platform"), 
        date = time_str.split(" ")[0],
        update_time = "",
    )

# 定时任务，每天早上执行一次，获取比赛信息
@scheduler.task("cron", id='get_contest_info', day="*", hour="*", minute="24", second="0")
def get_contest_info():
    with scheduler.app.app_context():
        # 先检查今天是不是获取过
        if DailyReportModel.query.filter_by(date=str(datetime.date.today())).first() is not None:
            return
        
        daily_report: list[dict] | None = contest_hunter.hunt_all()
        if daily_report is None:
            raise Exception("daily-report failed {:s}".format(str(datetime.datetime.now())))
        
        daily_report.sort(key=(lambda x: x.get('time', '')))
        results = list(map(transform_dict_to_contest, daily_report))
        print(datetime.date.today())
        db.session.add(DailyReportModel(date=str(datetime.date.today()), jsons=json.dumps(daily_report)))

        for contest in results:
            if Contest.query.filter(Contest.title == contest.title, Contest.platform == contest.platform).first() is None:
                db.session.add(contest)
        
        db.session.commit()