import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from pytz import timezone

# ContestHunter 是爬取网站比赛信息的基类，其他爬取具体网站的类继承该类并实现 hunt 方法
class ContestHunter:
    url = ""
    platform = ""
    headers = { # header 伪装
	    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
    }

    # 封装好的爬取页面的方法
    def GetHtmlText(self, url: str):
        try:
            # 等待 30s，再不相应算超时
            response = requests.get(url, timeout=30, headers=self.headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except:
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
        html = self.GetHtmlText(self.url).replace('<br />', '\n').replace('</p>', '\n')
        soup = BeautifulSoup(html, "html.parser")
        # 不知道为什么 soup print 出来是断掉的，但是可用
        # data-contestid 网页源代码 i 是大写，这里是小写，服了
        for contest in soup.find_all("tr", attrs={"data-contestid": True}):
            title = contest.find("td")

            # 只保留将要到来的比赛
            if title.string is None:
                continue
            
            contestInfo = {}
            # 比赛的名字
            contestInfo["title"] = title.string.strip()

            # 比赛的时间长度
            timeLength = title.find_next_sibling().find_next_sibling().find_next_sibling().string.strip()
            contestInfo["length"] = timeLength

            # 比赛的开始时间 格式为 Jul/07/2023 17:35
            startTime = contest.find("span", attrs={"class": "format-time"}).string
            # 转化为 Python 的标准格式
            contestDateTime = datetime.strptime(startTime, "%b/%d/%Y %H:%M")
            # print(contestDateTime)

            # 转换时区
            contestDateTime = self.convert_timezone(contestDateTime, 'Europe/Moscow', 'Asia/Shanghai')
            # 加入
            contestInfo["time"] = str(contestDateTime)

            result.append(contestInfo)
        
        return {"platform": "codeforces", "contests": result}

class AtcoderHunter(ContestHunter):
    url = "https://atcoder.jp/contests/"
    platform = "atcoder"

    def hunt(self):
        result = []
        html = self.GetHtmlText(self.url).replace('<br />', '\n').replace('</p>', '\n')
        soup = BeautifulSoup(html, "html.parser")

        contest_table = soup.find("div", attrs={"id": "contest-table-upcoming"})
        contest_table_tbody = contest_table.find("tbody") # 表单
        for contest in contest_table_tbody.find_all("tr"):
            # 开始时间，是日本的时间 "2023-07-08 21:00:00+0900"
            startTimeTag = contest.find("td", attrs={"class": "text-center"})
            startTime: str = startTimeTag.find("time", attrs={"class": "fixtime fixtime-full"}).string
            startTime = startTime.strip().split("+")[0]
            # print(startTime)
            contestDateTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S") # 注意两个参数别反了
            contestDateTime = self.convert_timezone(contestDateTime, 'Asia/Tokyo', 'Asia/Shanghai')

            # 比赛标题
            title = contest.find("a", attrs={"href": re.compile("/contests/[\w]+")}).string
            
            # 比赛持续时间
            timeLengthTag = startTimeTag.find_next_sibling("td", attrs={"class": "text-center"})
            timeLength = timeLengthTag.string

            # 比赛 rating 范围
            ratingTag = timeLengthTag.find_next_sibling("td", attrs={"class": "text-center"})
            rating = ratingTag.string

            contestInfo = {
                "time": str(contestDateTime), 
                "title": title,
                "length": timeLength,
                "rating": rating,    
            }

            result.append(contestInfo)

        return result

if __name__ == "__main__":
    result = AtcoderHunter().hunt()
    print(*result, sep="\n")