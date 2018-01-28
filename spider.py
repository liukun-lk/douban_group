#! /usr/bin/env python3

from cache import Cache
from lxml import etree
import config
import logging
import re
import requests
import time

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
            res = requests.get(url=url, headers=config.get_header(), timeout=config.TIMEOUT)
            return res.text
        except Exception:
            count = 0
            while count < config.RETRY_TIMES:
                try:
                    # TODO: 添加代理
                    res = requests.get(url=url, headers=config.get_header(), timeout=config.TIMEOUT)
                    return res.text
                except Exception:
                    count += 1
                    time.sleep(2**count)
        return None

    def parser(self, regx, body, multi=False):
        """解析元素， xpath 语法
        """
        if isinstance(body, bytes):
            body = etree.HTML(body)
        result = body.xpath(regx)
        if multi:
            return result
        return result[0] if result else None


    def _init_page_urls(self, group_list):
        """初始化需要抓取页面的URL

        @group_list, str, 小组URL
        """
        urls = []
        for page in range(config.MAX_PAGE):
            base_url = "{}{}".format(group_list, config.GROUP_SUFFIX)
            url = base_url.format(page * 25)
            urls.append(url)

        self.cache.r_sadd('group:index_urls:hz', urls)
        return urls

    def _crawl_page(self, url, group_name):
        """爬取帖子

        @url, str, 当前页面URL
        @group_name, str, 小组名称
        """
        logging.info("{} Processing page: {}".format(time.asctime(), url))
        # html = self.fetch(url)
        # self.cache.r_set('tmp:group:html', html)
        html = self.cache.r_get('tmp:group:html')
        lists = self.parser(self.__rules['topic_item'], html, True)
        new_topics, old_topics = self._get_page_info(lists, group_name)
        # TODO: 如果返回空或者4xx等错误，将URL添加到重试队列中。
        return new_topics, old_topics

    def _get_page_info(self, lists, group_name):
        """获取每一页的帖子的基本信息，并区分新旧帖，避免数据重复

        @lists, list, 当前页的帖子项
        @group_name, str, 小组名称
        """
        new_topics, old_topics, ids = [], [], []
        # 第一行是标题头,舍掉
        for list in lists[1:]:
            topic = {}
            topic['title'] = self.parser(self.__rules['title'], list)
            topic['author'] = self.parser(self.__rules['author'], list)
            topic['reply'] = self.parser(self.__rules['reply'], list) or 0
            topic['last_reply_time'] = self.parser(self.__rules['last_reply_time'], list)
            topic['url'] = self.parser(self.__rules['url'], list)
            now = time.asctime()
            topic['crawled_at'] = now
            topic['updated_at'] = now
            topic['topic_id'] = re.findall(r'(\d+)', topic['url'])[0]

            ids.append(topic['topic_id'])
            if self.cache.r_sismember('group:{}:topic_ids'.format(group_name), topic['topic_id']):
                old_topics.append(topic)
            else:
                new_topics.append(topic)

        self.cache.r_sadd('group:{}:topic_ids'.format(group_name), ids)
        return new_topics, old_topics

    def _crawl_detail(self, url):
        """爬取每个帖子的详细内容

        @url, str, 每个帖子的URL
        """
        logging.info("{} Processing topic: {}".format(time.asctime(), url))
        # TODO: 如果帖子已经存在，则不再进行爬取？

        # html = self.fetch(url)
        # self.cache.r_set('tmp:topic:html', html)
        html = self.cache.r_get('tmp:topic:html')
        topic = self._get_detail_info(html, url)
        # TODO: 如果返回空或者4xx等错误，将URL添加到重试队列中。

        return html

    def _get_detail_info(self, html, url):
        """获取帖子详情

        """
        if "机器人".encode() in html:
            logging.warn("{} 403.html".format(url))
            return None
        topic = {}
        title = self.parser(self.__rules['detail_title_sm'], html) \
                or self.parser(self.__rules['detail_title_lg'], html)
        if title is None:
            return None

        topic['title'] = title.strip()
        topic['url'] = url
        topic['crawled_at'] = time.asctime()
        topic['create_time'] = self.parser(self.__rules['create_time'], html)
        topic['author'] = self.parser(self.__rules['detail_author'], html)
        content = "\n".join(self.parser(self.__rules['content'], html, True))
        topic['content'] = content

        topic['images'] = self.parser(self.__rules['images'], html, True)

        # phone = re.findall(r'(1[3|5|7|8|][0-9]{8})', content)
        # topic['phone'] = '' if not phone else phone[0]

        # sns = re.findall(r'(微信|qq|QQ)号?(:|：|\s)?(\s)?([\d\w_一二两三四五六七八九零]{5,})', content)
        # topic['sns'] = '' if not sns else sns[0]

        # area = re.findall(r'((\d{1,3})(多)?[平|㎡])', content)
        # topic['area'] = '' if not area else ''.join(area[0])

        # modle = re.findall(r'([\d一二两三四五六七八九][居室房]([123一二两三]厅)?([12一二两]厨)?([1234一二两三四]卫)?([12一二两]厨)?)', content)
        # topic['model'] = ''

        return topic

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    spider = DoubanSpider()
    # html_body = spider.fetch("http://106.15.248.58")
    # # http://7u2ha0.com1.z0.glb.clouddn.com/reset_password.jpg
    # spider._init_page_urls("https://www.douban.com/group/145219/")
    # spider._crawl_page(config.TEST_URL)
    # print(spider._crawl_page("http://localhost:3000", 'hz'))
    # print(time.asctime())
    res = spider._crawl_detail("https://www.douban.com/group/topic/111003856/")
    print(spider._get_detail_info(res, "https://www.douban.com/group/topic/111003856/"))
