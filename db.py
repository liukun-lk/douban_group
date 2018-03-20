#! /usr/bin/env python3
from peewee import *
import datetime

db = SqliteDatabase('test.db')


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
        database = db


class Topic(Model):
    title = CharField()
    url = CharField()
    crawled_at = DateTimeField(default=datetime.datetime.now)
    create_time = DateTimeField(default=datetime.datetime.now)
    author = CharField()
    content = TextField()
    images = TextField()

    class Meta:
        database = db


def init_table():
    db.connect()
    db.create_tables([TopicList, Topic])
    db.close()


if __name__ == '__main__':
    init_table()
