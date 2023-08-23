# Contest Hunter 

一个 Flask 构建的 全网比赛日报后端

<!-- 目前支持 Codeforces 的比赛信息爬取 -->

时间线

- 2023/07/02：建立项目，确定框架，写了 Codeforces 的比赛信息爬取
- 2023/07/04: 添加了 Atcoder 的比赛信息爬取
- 2023/07/19: 将项目分离为多个文件
- 2023/07/25: 
    - 完善了 按照日期查询比赛的接口，添加了手动的 http 测试
    - 完善了 日报 接口
- 2023/08/15:
    - 添加了 Luogu 的比赛信息
    - 添加了新的爬虫方式
  
目前支持爬取的平台有

- codeforces
- atcoder
- nowcoder
- acwing
- luogu

将来可能要支持的

- codechef
- leetcode

## Daily Report API
### GET /daily-report

获取最新的日报信息。

**请求参数**

无

**响应**

200 OK：成功获取日报信息
```
{
  "status_code": "1",
  "data": {
    // 日报数据
  }
}
```

404 Not Found：当天没有日报信息
```
{
  "status_code": "0",
  "data": null
}
```

## Contest by Day API
### GET /contest-by-day
获取指定日期的比赛信息。

请求参数
```
{
  "date": "yyyy-mm-dd"
}
```
date (必需)：指定的日期，格式为 yyyy-mm-dd。

**响应**

200 OK：成功获取比赛信息
```
{
  "status_code": "1",
  "data": [
    // 比赛信息列表
  ]
}
```
404 Not Found：指定日期没有比赛信息
```
{
  "status_code": "0",
  "data": null
}
```
