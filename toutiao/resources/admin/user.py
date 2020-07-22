from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask import g, current_app
from sqlalchemy.exc import IntegrityError
import time

from utils.decorators import login_required, set_db_to_read
from utils import parser
from models import db
from models.news import Attitude, ArticleStatistic, CommentLiking, Comment
from cache import statistic as cache_statistic


class CommentLikingListResource(Resource):
    """
    评论点赞
    """
    method_decorators = [set_db_to_read, login_required]

    def post(self):
        """
        评论点赞
        """
        json_parser = RequestParser()
        json_parser.add_argument('page', type=parser.comment_id, required=True, location='args')
        json_parser.add_argument('per_page', type=parser.comment_id, required=True, location='args')
        args = json_parser.parse_args()
        target = args.target
        ret = 1
        try:
            comment_liking = CommentLiking(user_id=g.user_id, comment_id=target)
            db.session.add(comment_liking)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            ret = CommentLiking.query.filter_by(user_id=g.user_id, comment_id=target, is_deleted=True) \
                .update({'is_deleted': False})
            db.session.commit()

        if ret > 0:
            cache_statistic.CommentLikingCountStorage.incr(target)
        return {'target': target}, 201

