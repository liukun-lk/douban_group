#! /usr/bin/env python3

# DouBan group url lists.
GROUP_LISTS = {"hz1": "https://www.douban.com/group/145219/"}
# paginate url query
GROUP_SUFFIX = "discussion?start={}"
# crawl 5 pages
MAX_PAGE = 5
# match rules
RULES = {
    # 每个帖子项
    "topic_item": "//table[@class='olt']/tr",
    "url_list": "//table[@class='olt']/tr/td[@class='title']/a/@href",
    # 列表元素
    "title": "td[@class='title']/a/@title",
    "author": "td[@nowrap='nowrap'][1]/a/text()",
    "reply": "td[@nowrap='nowrap'][2]/text()",
    "last_reply_time": "td[@class='time']/text()",
    "url": "td[@class='title']/a/@href",
    # 帖子详情
    "detail_title_sm": "//td[@class='tablecc']/text()",
    # 完整标题
    "detail_title_lg": "//div[@id='content']/h1/text()",
    "create_time": "//span[@class='color-green']/text()",
    "detail_author": "//span[@class='from']/a/text()",
    "content": "//div[@class='topic-content']/p/text()",
    "content_text": "//div[@class='topic-content']//text()",
    "images": "//*[@id='link-report']//img/@src",
}
# 并发数
POOL_SIZE = 20
# 监控周期(秒),默认10分钟
WATCH_INTERVAL = 10 * 60
# 重载代理周期
PROXY_INTERVAL = 30 * 60
# 请求超时时间
TIMEOUT = 3
# 请求重试次数
RETRY_TIMES = 3
# test data
TEST_URL = "https://www.douban.com/group/145219/discussion?start=0"
# 请求返回 403 最大次数
MAX_403_NUMBER = 10
