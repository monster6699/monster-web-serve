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


class ArticleCreateResourece(Resource):
    """
    创建菜单
    """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def post():
        json_parser = RequestParser()
        json_parser.add_argument('categories', type=int, required=True, location='json')
        json_parser.add_argument('content', type=str, required=True, location='json')
        json_parser.add_argument('imageFiles', type=str, required=True, location='json')
        json_parser.add_argument('title', type=str, required=True, location='json')

        args = json_parser.parse_args()
        try:
            cover = Cover(title=args.title, image=args.imageFiles)
            db.session.add(cover)
            db.session.commit()
            content = Content(content=args.content, category_id=args.categories, cover_id=cover.id)
            db.session.add(content)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            db.session.commit()
            return {"message": 'add error'}, 405
        return "ok"
