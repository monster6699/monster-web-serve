import json
import random

from flask import current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy import func
import time

from models.article import Category
from utils.decorators import login_required, set_db_to_read, set_db_to_write


class GetCatergoryResourece(Resource):
    """
    创建菜单
    """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def get():
        catergory_list = Category.query.all()
        data = []
        for catergory in catergory_list:
            data.append({
                "id": catergory.id,
                "name": catergory.name,
                "status": catergory.status
            })
        return data
