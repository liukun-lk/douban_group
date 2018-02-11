#! /usr/bin/env python3

from peewee import *

db = SqliteDatabase('test.db')

class Person(Model):
    name = CharField()
    birthday = DateField()
    is_relative = BooleanField()

    class Meta:
        database = db

def init_table():
    db.connect()
    db.create_tables([Person])

if __name__ == '__main__':
    init_table()