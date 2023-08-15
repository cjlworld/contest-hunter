import re
import requests
import traceback
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Tag
from pytz import timezone
from playwright.sync_api import Playwright, sync_playwright, expect

"""
    为了将 contest_hunter 模块和其他模块解耦，
    contest_hunter 统一返回字典信息，格式为 [{比赛1}, {比赛2}]
    由 scheduler 转译为 Contest 类
"""

# PageHunter 是爬取页面的基类
class PageCrawler:
    @classmethod
    def crawl(cls, url: str) -> str:
        pass

class PlayWrightPageCrawler(PageCrawler):
    @classmethod
    def crawl(cls, url: str) -> str:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            return page.content()

class RequestsPageCrawler(PageCrawler):
    headers: dict[str, str] = { # header
    }
    @classmethod
    def crawl(cls, url: str) -> str:
        try:
            # 等待 30s，再不相应算超时
            response = requests.get(url, timeout=30, headers=cls.headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except:
            print("RequestsPageCrawler.crawl failed")
            return ""

# ContestHunter 是爬取网站比赛信息的基类，其他爬取具体网站的类继承该类并实现 hunt 方法
class ContestHunter:
    url = ""
    platform = ""
    
    def __init__(self, page_crawler: PageCrawler) -> None:
        self.page_crawler = page_crawler

    # 转换时区
    @staticmethod
    def convert_timezone(Atime: datetime, Aplace: str, Bplace: str) -> datetime:
        return Atime.replace(tzinfo=timezone(Aplace)).astimezone(timezone(Bplace))

    # 获取比赛信息，由 子类实现
    def hunt(self) -> list:
        return []

# Codeforces
class CodeforcesHunter(ContestHunter):
    url = "https://codeforces.com/contests"
    platform = "codeforces"

    def hunt(self):
        result = []
        html = self.page_crawler.crawl(self.url).replace('<br />', '\n').replace('</p>', '\n')
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

# AtCoder
class AtcoderHunter(ContestHunter):
    url = "https://atcoder.jp/contests/"
    platform = "atcoder"

    def hunt(self):
        result = []
        html = self.page_crawler.crawl(self.url).replace('<br />', '\n').replace('</p>', '\n')
        soup = BeautifulSoup(html, "html.parser")

        contest_table = soup.find("div", attrs={"id": "contest-table-upcoming"})
        if contest_table is None:
            raise ValueError('A very specific bad thing happened.')
        contest_table_tbody = contest_table.find("tbody") # 表单
        if type(contest_table_tbody) is not Tag:
            raise ValueError('A very specific bad thing happened.')
        
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
                "title": title,
                "time": str(contest_datetime), 
                "length": time_length,
                "rating": rating,    
                "platform": self.platform,
            }

            result.append(contest_info)

        return result

# AcWing
class AcwingHunter(ContestHunter):
    url = "https://www.acwing.com/activity/1/competition/"
    platform = "acwing"

    def hunt(self):
        result = []
        html = self.page_crawler.crawl(self.url).replace('<br />', '\n').replace('</p>', '\n')
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
                "title": "Acwing " + title,
                "time": start_time,
                "platform": self.platform,
            }

            result.append(contest_info)

        return result

# NowCoder
class NowCoderHunter(ContestHunter):
    url = "https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter="
    url_1 = url + "13"
    url_2 = url + "14"

    platform = "nowcoder"

    def hunt_page(self, url: str) -> list:
        result: list[dict[str, str]] = []
        html = self.page_crawler.crawl(url=url).replace('<br />', '\n').replace('</p>', '\n')
        soup = BeautifulSoup(html, "html.parser")

        for contest_tag in soup.find_all("div", attrs={"class": "platform-item-cont"}):
            if contest_tag.find("span", attrs={"class": "match-status match-end-tag"}) is not None:
                continue
            
            contest_info = {}
            # breakpoint()
            contest_title_tag = contest_tag.find("a", attrs={"href": re.compile("/acm/contest/[\w]+")})
            contest_info["title"] = contest_title_tag.string

            contest_time_tag = contest_tag.find("li", attrs={"class": "match-time-icon"})

            contest_time_str = contest_time_tag.string.split("(")[0]
            # print(contest_time_str.lstrip("比赛时间： ").split(" 至 "))
            start_time, end_time = map(lambda x: datetime.strptime(x.strip(), "%Y-%m-%d %H:%M"), 
                                       contest_time_str.lstrip("比赛时间： ").split(" 至 "))
            contest_info["time"] = str(start_time)

            contest_length = end_time - start_time
            contest_info["length"] = str(contest_length)

            contest_info["platform"] = self.platform
            result.append(contest_info)

        return result

    def hunt(self) -> list:
        result: list[dict[str, str]] = []
        result.extend(self.hunt_page(self.url_1))
        result.extend(self.hunt_page(self.url_2))
        return result

# Luogu
class LuoguContestHunter(ContestHunter):
    url = "https://www.luogu.com.cn/contest/list"
    platform = "luogu"

    def hunt(self) -> list:
        result: list[dict[str, str]] = []
        html = self.page_crawler.crawl(url=self.url).replace('<br />', '\n').replace('</p>', '\n')
        soup = BeautifulSoup(html, "html.parser")

        for contest_tag in soup.find_all("div", attrs={"data-v-3ae85f6d": True, 
                                                       "data-v-24f898d2": True}):
            
            status_tag = contest_tag.find("span", attrs={"class": "status"})
            # 已结束
            if status_tag is None or status_tag.string.strip() == "已结束":
                continue
            
            # print(status_tag)
            contest_info = {}

            title_tag = contest_tag.find("a", attrs={"target": "_blank"})
            contest_info["title"] = title_tag.string.strip()

            time_tag = contest_tag.find("span", attrs={"class": "time"})
            # print(time_tag)
            time_tags = time_tag.find_all("time")
            # print(time_tags)

            date_str, time_start_str = time_tags[0].string.split()
            time_end_str = time_tags[1].string

            date_str = str(datetime.now().year) + "-" + date_str

            start_datetime = datetime.strptime(date_str + " " + time_start_str, "%Y-%m-%d %H:%M")
            end_datetime =  datetime.strptime(date_str + " " + time_end_str, "%Y-%m-%d %H:%M")

            # print(start_datetime)
            # print(end_datetime)

            contest_info["time"] = str(start_datetime)
            contest_info["length"] = str(end_datetime-start_datetime)

            contest_info["platform"] = self.platform

            result.append(contest_info)

        return result


# 由爬取网站对象组成的字典（更新程序调用 hunt() 方法获取信息）
# 加入网站后在字典中加入相应的键值对
contest_hunter_dict = {
    "codeforces": CodeforcesHunter(RequestsPageCrawler()),
    "atcoder": AtcoderHunter(RequestsPageCrawler()),
    "acwing": AcwingHunter(RequestsPageCrawler()),
    "nowcoder": NowCoderHunter(RequestsPageCrawler()),
    "luogu": LuoguContestHunter(PlayWrightPageCrawler()),
}

def hunt_all() -> list | None:
    """
    失败返回 None
    """
    results = []
    try:
        for key, val in contest_hunter_dict.items():
            results.extend(val.hunt())
    except Exception as err:
        traceback.print_exc()
        return None
    
    return results

if __name__ == "__main__":
    results = hunt_all()
    if results is not None:
        print(*results, sep='\n')
    else:
        print("failed")
    # print(contest_hunter_dict["luogu"].hunt())