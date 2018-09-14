#! /usr/bin/env python3
from peewee import *
import datetime

mysql_db = MySQLDatabase(
    "douban_spider", user="root", password="", host="127.0.0.1", port=3306
)


class TopicList(Model):
    author          = CharField()
    crawled_at      = DateTimeField(default=datetime.datetime.now)
    last_reply_time = DateTimeField(default=datetime.datetime.now)
    reply           = IntegerField()
    title           = CharField()
    topic_id        = IntegerField()
    updated_at      = DateTimeField(default=datetime.datetime.now)
    url             = CharField()

    class Meta:
        database = mysql_db


class Topic(Model):
    author      = CharField()
    content     = TextField()
    crawled_at  = DateTimeField(default=datetime.datetime.now)
    create_time = DateTimeField(default=datetime.datetime.now)
    images      = TextField()
    title       = CharField()
    topic_id    = IntegerField()
    url         = CharField()

    class Meta:
        database = mysql_db


if __name__ == "__main__":
    pass
