#! /usr/bin/env python3

import json
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse, abort
from db import TopicList, Topic
from playhouse.shortcuts import model_to_dict

import logging

logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):

    def get(self):
        return {"hello": "world"}


class TopicLists(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("page", type=int, required=False, default=1)
        self.reqparse.add_argument("per", type=int, required=False, default=10)
        super().__init__()

    def get(self):
        args = self.reqparse.parse_args()
        topic_lists = [
            model_to_dict(list)
            for list in TopicList.select().paginate(args["page"], args["per"])
        ]
        meta = {"count": TopicList.select().count()}

        return jsonify({"topic_lists": topic_lists, "meta": meta})


class SingleTopic(Resource):

    def get(self, topic_id):
        try:
            topic = Topic.get(Topic.topic_id == topic_id)

            topic_dict = model_to_dict(topic)
            topic_dict["images"] = topic_dict["images"].split(",")
            return jsonify(topic_dict)
        except:
            abort(404, message="Topic id {} is not found".format(topic_id))


api.add_resource(HelloWorld, "/")
api.add_resource(SingleTopic, "/api/topics/<int:topic_id>")
api.add_resource(TopicLists, "/api/topic_lists")


if __name__ == "__main__":
    app.run(debug=True)
