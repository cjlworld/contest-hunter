import requests
from datetime import datetime
from bs4 import BeautifulSoup
from pytz import timezone

# ContestHunter 是爬取网站比赛信息的基类，其他爬取具体网站的类继承该类并修改 hunt 方法
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
            contestDateTime = contestDateTime.replace(tzinfo=timezone('Europe/Moscow')).astimezone(timezone("Asia/Shanghai"))
            # 加入
            contestInfo["time"] = str(contestDateTime)

            result.append(contestInfo)
        
        return {"platform": "codeforces", "contests": result}

if __name__ == "__main__":
    result = CodeforcesHunter().hunt()
    print(result)