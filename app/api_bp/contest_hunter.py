import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from pytz import timezone

"""
    为了将 contest_hunter 模块和其他模块解耦，
    contest_hunter 统一返回字典信息，格式为 [{比赛1}, {比赛2}]
    由 scheduler 转译为 Contest 类
"""

# ContestHunter 是爬取网站比赛信息的基类，其他爬取具体网站的类继承该类并实现 hunt 方法
class ContestHunter:
    url = ""
    platform = ""
    headers = { # header 伪装
    }

    # 封装好的爬取页面的方法
    def get_html_text(self, url: str):
        try:
            # 等待 30s，再不相应算超时
            response = requests.get(url, timeout=30, headers=self.headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except:
            print("failed")
            return ""
    
    # 转换时区
    def convert_timezone(self, Atime: datetime, Aplace: str, Bplace: str) -> datetime:
        return Atime.replace(tzinfo=timezone(Aplace)).astimezone(timezone(Bplace))

    # 获取比赛信息，由 子类实现
    def hunt(self):
        pass

# Codeforces
class CodeforcesHunter(ContestHunter):
    url = "https://codeforces.com/contests"
    platform = "codeforces"

    def hunt(self):
        result = []
        html = self.get_html_text(self.url).replace('<br />', '\n').replace('</p>', '\n')
        soup = BeautifulSoup(html, "html.parser")
        # 不知道为什么 soup print 出来是断掉的，但是可用
        # data-contestid 网页源代码 i 是大写，这里是小写，服了
        for contest in soup.find_all("tr", attrs={"data-contestid": True}):
            title = contest.find("td")

            # 只保留将要到来的比赛
            if title.string is None:
                continue
            
            contest_info = {}
            # 比赛的名字
            contest_info["title"] = title.string.strip()

            # 比赛的时间长度
            time_length = title.find_next_sibling().find_next_sibling().find_next_sibling().string.strip()
            contest_info["length"] = time_length

            # 比赛的开始时间 格式为 Jul/07/2023 17:35
            start_time = contest.find("span", attrs={"class": "format-time"}).string
            # 转化为 Python 的标准格式
            contest_datetime = datetime.strptime(start_time, "%b/%d/%Y %H:%M")
            # print(contest_datetime)

            # 转换时区
            contest_info["time"] = str(self.convert_timezone(contest_datetime, 'Etc/GMT-3', 'Etc/GMT-8'))

            contest_info["platform"] = self.platform
            result.append(contest_info)
        
        return result

class AtcoderHunter(ContestHunter):
    url = "https://atcoder.jp/contests/"
    platform = "atcoder"

    def hunt(self):
        result = []
        html = self.get_html_text(self.url).replace('<br />', '\n').replace('</p>', '\n')
        soup = BeautifulSoup(html, "html.parser")

        contest_table = soup.find("div", attrs={"id": "contest-table-upcoming"})
        contest_table_tbody = contest_table.find("tbody") # 表单
        for contest in contest_table_tbody.find_all("tr"):
            # 开始时间，是日本的时间 "2023-07-08 21:00:00+0900"
            start_time_tag = contest.find("td", attrs={"class": "text-center"})
            start_time: str = start_time_tag.find("time", attrs={"class": "fixtime fixtime-full"}).string
            start_time = start_time.strip().split("+")[0]
            # print(start_time)
            contest_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") # 注意两个参数别反了
            contest_datetime = self.convert_timezone(contest_datetime, 'Etc/GMT-9', 'Etc/GMT-8')

            # 比赛标题
            title = contest.find("a", attrs={"href": re.compile("/contests/[\w]+")}).string
            
            # 比赛持续时间
            time_length_tag = start_time_tag.find_next_sibling("td", attrs={"class": "text-center"})
            time_length = time_length_tag.string

            # 比赛 rating 范围
            ratingTag = time_length_tag.find_next_sibling("td", attrs={"class": "text-center"})
            rating = ratingTag.string

            contest_info = {
                "time": str(contest_datetime), 
                "title": title,
                "length": time_length,
                "rating": rating,    
                "platform": self.platform,
            }

            result.append(contest_info)

        return result

class AcwingHunter(ContestHunter):
    url = "https://www.acwing.com/activity/1/competition/"
    platform = "acwing"

    def hunt(self):
        result = []
        html = self.get_html_text(self.url).replace('<br />', '\n').replace('</p>', '\n')
        soup = BeautifulSoup(html, "html.parser")

        for contest in soup.find_all("div", attrs={"class": "activity-index-block"}):
            status_tag = contest.find("span", attrs={"class": "btn btn-warning activity_status"})

            if status_tag is None: # 比赛已结束
                continue
            
            # 开始时间
            start_time_tag = contest.find_all("span", attrs={"class": "activity_td"})[-1]
            start_time = start_time_tag.string

            # 比赛标题
            title_tag = contest.find("span", attrs={"class": "activity_title"})
            title = title_tag.string

            contest_info = {
                "time": start_time,
                "title": title,
                "platform": self.platform,
            }

            result.append(contest_info)

        return result

# 由爬取网站对象组成的字典（更新程序调用 hunt() 方法获取信息）
# 加入网站后在字典中加入相应的键值对
contest_hunter_dict = {
    "codeforces": CodeforcesHunter(),
    "atcoder": AtcoderHunter(),
    "acwing": AcwingHunter(),
}

def hunt_all():
    results = []
    for key, val in contest_hunter_dict.items():
        results.extend(val.hunt())
    return results

if __name__ == "__main__":
    print(*hunt_all(), sep='\n')