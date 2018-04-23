#! /usr/bin/env python3
from cache import Cache
import config
import datetime
import logging
import re
import time
from random import random
from requests_html import HTMLSession, user_agent
from db import db, TopicList, Topic

session = HTMLSession()
user_agent("google chrome")


class DoubanSpider(object):

    def __init__(self):
        self.__group_list = config.GROUP_LISTS
        self.__suffix = config.GROUP_SUFFIX
        self.__rules = config.RULES
        self.cache = Cache()

    def fetch(self, url):
        """ HTTP request

        @url, str
        """
        try:
            time.sleep(random() * 1)
            res = session.get(url)
            if res.status_code == 200:
                return res.html
            else:
                return None

        except Exception:
            count = 0
            while count < config.RETRY_TIMES:
                try:
                    # TODO: 添加代理
                    res = session.get(url)
                    return res.html

                except Exception:
                    count += 1
                    time.sleep(2 ** count)
        return None

    def parser(self, regx, html, first=False):
        """解析元素， xpath 语法
        """
        return html.xpath(regx, first=first)

    def _init_page_urls(self, group_name):
        """初始化需要抓取页面的URL

        @group_list, str, 小组URL
        """
        urls = []
        for page in range(config.MAX_PAGE):
            base_url = "{}{}".format(self.__group_list["hz1"], config.GROUP_SUFFIX)
            url = base_url.format(page * 25)
            urls.append(url)
        # self.cache.r_sadd("group:{}:hz".format(group_name), urls)
        return urls

    def _crawl_page(self, url, group_name):
        """爬取帖子

        @url, str, 当前页面URL
        @group_name, str, 小组名称
        """
        logging.info("{} Processing page: {}".format(time.asctime(), url))
        # if self.cache.r_get_number(
        #     "group:{}:incr".format(group_name)
        # ) >= config.MAX_403_NUMBER:
        #     logging.warn("{} Request has been block: {}".format(time.asctime(), url))
        #     # return -1 will off redis pop new url to crawl page
        #     return -1
        html = self.fetch(url)
        if html is None:
            return [], []
        # self.cache.r_set('tmp:group:html', html)
        # html = self.cache.r_get('tmp:group:html')
        new_topics, old_topics = self._get_page_info(html, group_name, url)
        return new_topics, old_topics

    def _get_page_info(self, html, group_name, url):
        """获取每一页的帖子的基本信息，并区分新旧帖，避免数据重复

        @lists, list, 当前页的帖子项
        @group_name, str, 小组名称
        """
        if "机器人".encode() in html:
            logging.warn("{} 403.html".format(url))
            self.cache.r_sadd("group:{}:403".format(group_name), url)
            return None

        new_topics, old_topics, ids = [], [], []
        lists = html.xpath(self.__rules["topic_item"])
        # 第一行是标题头,舍掉
        for list in lists[1:]:
            topic = {}
            info = list.text.split("\n")
            if len(info) == 3:
                info.insert(2, "0")
            # ['话题', '作者', '回应', '最后回应']
            topic["title"] = info[0]
            topic["author"] = info[1]
            topic["reply"] = info[2]
            topic["last_reply_time"] = '-'.join([str(datetime.date.today().year), info[3] + ':00']) # 2018-03-17 21:03:00
            # requests-html lib first return soup_parse object :(
            topic["url"] = list.lxml.cssselect("tr td.title a")[0].get("href")
            now = time.asctime()
            topic["crawled_at"] = now
            topic["updated_at"] = now
            topic["topic_id"] = re.findall(r"(\d+)", topic["url"])[0]
            ids.append(topic["topic_id"])
            if self.cache.r_sismember(
                "group:{}:topic_ids".format(group_name), topic["topic_id"]
            ):
                old_topics.append(topic)
            else:
                new_topics.append(topic)
                with db.atomic():
                    TopicList.create(**topic)
        self.cache.r_sadd("group:{}:topic_ids".format(group_name), ids)
        return new_topics, old_topics

    def _crawl_detail(self, group_name, url):
        """爬取每个帖子的详细内容

        @url, str, 每个帖子的URL
        """
        logging.info("{} Processing topic: {}".format(time.asctime(), url))
        # TODO: 如果帖子已经存在，则不再进行爬取？
        # if self.cache.r_get_number(
        #     "group:{}:incr".format(group_name)
        # ) >= config.MAX_403_NUMBER:
        #     logging.warn("{} Request has been block: {}".format(time.asctime(), url))
        #     # return -1 will off redis pop new url to crawl page
        #     return -1
        html = self.fetch(url)
        if html is None:
            return None
        # self.cache.r_set('tmp:topic:html', html)
        # html = self.cache.r_get('tmp:topic:html')
        topic = self._persist_detail_info(html, group_name, url)
        return html

    def _persist_detail_info(self, html, group_name, url):
        """获取帖子详情

        """
        if "机器人".encode() in html:
            logging.warn("{} 403.html".format(url))
            self.cache.r_sadd("group:{}:403".format(group_name), url)
            return None

        topic = {}
        images = []
        title = self.parser(self.__rules["detail_title_lg"], html, True) or self.parser(
            self.__rules["detail_title_sm"], html, True
        )
        if title is None:
            return None

        topic["title"] = title.strip()
        topic["url"] = url
        topic["crawled_at"] = time.asctime()
        topic["create_time"] = self.parser(self.__rules["create_time"], html, True)
        topic["author"] = self.parser(self.__rules["detail_author"], html, True)
        content = "\n".join(self.parser(self.__rules["content"], html))
        if content is not "":
            topic["content"] = content
        else:
            content = "\n".join(self.parser(self.__rules["content_text"], html))
            topic["content"] = content
        images.extend(self.parser(self.__rules["images"], html))
        if len(images) > 0:
            topic["images"] = ",".join(images)
        else:
            topic["images"] = ""
        # phone = re.findall(r'(1[3|5|7|8|][0-9]{8})', content)
        # topic['phone'] = '' if not phone else phone[0]
        # sns = re.findall(r'(微信|qq|QQ)号?(:|：|\s)?(\s)?([\d\w_一二两三四五六七八九零]{5,})', content)
        # topic['sns'] = '' if not sns else sns[0]
        # area = re.findall(r'((\d{1,3})(多)?[平|㎡])', content)
        # topic['area'] = '' if not area else ''.join(area[0])
        # modle = re.findall(r'([\d一二两三四五六七八九][居室房]([123一二两三]厅)?([12一二两]厨)?([1234一二两三四]卫)?([12一二两]厨)?)', content)
        # topic['model'] = ''
        with db.atomic():
            Topic.create(**topic)
        return topic

    def run(self):
        group_name = "hz1"
        topic_list_urls = self._init_page_urls(group_name)
        for url in topic_list_urls:
            new_topics, old_topics = self._crawl_page(url, group_name)
            for topic in new_topics:
                self._crawl_detail(group_name, topic["url"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    spider = DoubanSpider()
    spider.run()
# spider._init_page_urls("https://www.douban.com/group/145219/")
# spider._crawl_page(config.TEST_URL)
# lists = session.get("https://www.douban.com/group/145219/discussion?start=0").html.xpath(config.RULES['topic_item'], first=False)
# for list in lists[1:]:
# print(list.lxml.cssselect('tr td.title a'))
# print(spider._crawl_page("https://www.douban.com/group/145219/discussion?start=0", 'hz1'))
# print(time.asctime())
# res = spider._crawl_detail("hz1", "https://www.douban.com/group/topic/113860482/")
# print(spider._get_detail_info(res, 'hz', "https://www.douban.com/group/topic/111003856/"))
# print(spider._init_page_urls('hz1'))
