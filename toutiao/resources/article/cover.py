import json
import random

from flask import current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy import func
import time

from models.article import Content, Cover
from utils.decorators import login_required, set_db_to_read, set_db_to_write
from models import db


class ArticleCoverListResourece(Resource):
    """
    创建菜单
    """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def get():
        data = []
        cover_list = Cover.query.all()
        for cover in cover_list:
            data.append({
                "id": cover.id,
                "title": cover.title,
                "image": cover.image.split(",") if cover.image else ""
            })
        return data
