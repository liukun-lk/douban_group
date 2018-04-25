#! /usr/bin/env python3
from peewee import *
import datetime

mysql_db = MySQLDatabase(
    "douban_spider", user="root", password="", host="127.0.0.1", port=3306
)


class TopicList(Model):
    title = CharField()
    author = CharField()
    reply = IntegerField()
    last_reply_time = DateTimeField(default=datetime.datetime.now)
    url = CharField()
    crawled_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    topic_id = IntegerField()

    class Meta:
        database = mysql_db


class Topic(Model):
    title = CharField()
    url = CharField()
    crawled_at = DateTimeField(default=datetime.datetime.now)
    create_time = DateTimeField(default=datetime.datetime.now)
    author = CharField()
    content = TextField()
    images = TextField()

    class Meta:
        database = mysql_db


def init_table():
    mysql_db.connect()
    mysql_db.create_tables([TopicList, Topic])
    mysql_db.close()


if __name__ == "__main__":
    init_table()
