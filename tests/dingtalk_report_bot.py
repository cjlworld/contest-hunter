import os
import json
import requests
import datetime
from functools import cmp_to_key
from dingtalkchatbot.chatbot import DingtalkChatbot

# 将打卡结果发送到 Dingding
def send_to_ding(text: str) -> None:
    """
        从环境变量中获取 DING_WEBHOOK 和 DING_SECRET
    """
    DING_WEBHOOK = os.getenv("DING_WEBHOOK") # webhook
    DING_SECRET = os.getenv("DING_SECRET")   # 加签

    if DING_SECRET is None:
        raise Exception("DING_SECRET is None")
    if DING_WEBHOOK is None:
        raise Exception("DING_WEBHOOK is None")

    dingbot = DingtalkChatbot(webhook=DING_WEBHOOK, secret = DING_SECRET) 
    dingbot.send_markdown(title = "您收到一份来自 contest-hunter 的报告，请查收！", 
                          text = text, 
                          is_at_all = False)

CONTEST_HUNTER_BASE_URL = os.getenv("CONTEST_HUNTER_BASE_URL")

def get_report() -> str:
    today: str = str(datetime.date.today())

    try:
        if CONTEST_HUNTER_BASE_URL is None:
            raise Exception("CONTEST_HUNTER_BASE_URL is None")
        
        response = requests.get(url=CONTEST_HUNTER_BASE_URL+"daily-report", data = {"date" : today})

        response_json = json.loads(response.text)
        if response_json.get("status_code") == "0":
            raise Exception("status_code: 0")
    except Exception as err:
        print(err)
        return "**全网比赛日报出错，请尽快检修！**"

    contests: list[dict[str, str]] = response_json.get("data")

    text = "## 全网比赛日报 " + str(datetime.date.today()) + "\n\n***\n"
    contests.sort(key=(lambda x: x.get("time", "").split(" ")[0]))
    for contest in contests:
        text += contest.get("title", "")
        text += "\n\n"

        for key, val in contest.items():
            if key == "title":
                continue
    
            text += "- {:s}: {:s}\n".format(key, val)
        
        text += "***\n"
    text = text.rstrip("***\n")
    return text

if __name__ == "__main__":
    text: str = get_report()
    print(text)
    send_to_ding(text=text)
