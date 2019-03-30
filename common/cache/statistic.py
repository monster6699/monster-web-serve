from flask import current_app
from sqlalchemy import func

from redis.exceptions import RedisError, ConnectionError
from models.news import Article, Collection, Attitude, CommentLiking, Comment
from models.user import Relation
from models import db


class CountStorageBase(object):
    """
    数据存储父类
    """
    key = ''

    @classmethod
    def get(cls, id_value):
        """
        获取
        """
        try:
            count = current_app.redis_master.zscore(cls.key, id_value)
        except ConnectionError as e:
            current_app.logger.error(e)
            try:
                count = current_app.redis_slave.zscore(cls.key, id_value)
            except RedisError as e:
                current_app.logger.error(e)
                count = 0

        count = 0 if count is None else int(count)

        return count

    @classmethod
    def incr(cls, id_value, increment=1):
        """
        增加
        """
        try:
            current_app.redis_master.zincrby(cls.key, id_value, increment)
        except RedisError as e:
            current_app.logge.error(e)

    @classmethod
    def reset(cls, redis_client, *items):
        """
        重置数值，用于定时任务纠偏使用
        """
        pl = redis_client.pipeline()
        pl.delete(cls.key)
        pl.zadd(cls.key, *items)
        pl.execute()


class ArticleReadingCountStorage(CountStorageBase):
    """
    文章阅读量
    """
    key = 'count:art:reading'


class UserArticlesReadingCountStorage(CountStorageBase):
    """
    作者的文章阅读总量
    """
    kye = 'count:user:arts:reading'


class UserArticlesCountStorage(CountStorageBase):
    """
    用户文章数量
    """
    key = 'count:user:arts'

    @classmethod
    def db_query(cls):
        ret = db.session.query(Article.user_id, func.count(Article.id)) \
            .filter(Article.status == Article.STATUS.APPROVED).group_by(Article.user_id).all()
        return ret


class ArticleCollectingCountStorage(CountStorageBase):
    """
    文章收藏数量
    """
    key = 'count:art:collecting'

    @classmethod
    def db_query(cls):
        ret = db.session.query(Collection.article_id, func.count(Collection.article_id)) \
            .filter(Collection.is_deleted == 0).group_by(Collection.article_id).all()
        return ret


class UserArticleCollectingCountStorage(CountStorageBase):
    """
    用户收藏数量
    """
    key = 'count:user:art:collecting'

    @classmethod
    def db_query(cls):
        ret = db.session.query(Collection.user_id, func.count(Collection.article_id)) \
            .filter(Collection.is_deleted == 0).group_by(Collection.user_id).all()
        return ret


class ArticleDislikeCountStorage(CountStorageBase):
    """
    文章不喜欢数据
    """
    key = 'count:art:dislike'

    @classmethod
    def db_query(cls):
        ret = db.session.query(Attitude.article_id, func.count(Collection.article_id)) \
            .filter(Attitude.attitude == Attitude.ATTITUDE.DISLIKE).group_by(Collection.article_id).all()
        return ret


class ArticleLikingCountStorage(CountStorageBase):
    """
    文章点赞数据
    """
    key = 'count:art:liking'

    @classmethod
    def db_query(cls):
        ret = db.session.query(Attitude.article_id, func.count(Collection.article_id)) \
            .filter(Attitude.attitude == Attitude.ATTITUDE.LIKING).group_by(Collection.article_id).all()
        return ret


class CommentLikingCountStorage(CountStorageBase):
    """
    评论点赞数据
    """
    key = 'count:comm:liking'

    @classmethod
    def db_query(cls):
        ret = db.session.query(CommentLiking.comment_id, func.count(CommentLiking.comment_id)) \
            .filter(CommentLiking.is_deleted == 0).group_by(CommentLiking.comment_id).all()
        return ret


class ArticleCommentCountStorage(CountStorageBase):
    """
    文章评论数量
    """
    key = 'count:art:comm'

    @classmethod
    def db_query(cls):
        ret = db.session.query(Comment.article_id, func.count(Comment.id)) \
            .filter(Comment.status == Comment.STATUS.APPROVED).group_by(Comment.article_id).all()
        return ret


class CommentReplyCountStorage(CountStorageBase):
    """
    评论回复数量
    """
    key = 'count:art:reply'

    @classmethod
    def db_query(cls):
        ret = db.session.query(Comment.parent_id, func.count(Comment.id)) \
            .filter(Comment.status == Comment.STATUS.APPROVED, Comment.parent_id != None)\
            .group_by(Comment.parent_id).all()
        return ret


class UserFollowingsCountStorage(CountStorageBase):
    """
    用户关注数量
    """
    key = 'count:user:followings'

    @classmethod
    def db_query(cls):
        ret = db.session.query(Relation.user_id, func.count(Relation.target_user_id)) \
            .filter(Relation.relation == Relation.RELATION.FOLLOW)\
            .group_by(Relation.user_id).all()
        return ret


class UserFollowersCountStorage(CountStorageBase):
    """
    用户粉丝数量
    """
    key = 'count:user:followers'

    @classmethod
    def db_query(cls):
        ret = db.session.query(Relation.target_user_id, func.count(Relation.user_id)) \
            .filter(Relation.relation == Relation.RELATION.FOLLOW) \
            .group_by(Relation.target_user_id).all()
        return ret


class UserLikedCountStorage(CountStorageBase):
    """
    用户被赞数量
    """
    key = 'count:user:liked'

    @classmethod
    def db_query(cls):
        ret = db.session.query(Article.user_id, func.count(Attitude.id)).join(Attitude.article) \
            .filter(Attitude.attitude == Attitude.ATTITUDE.LIKING) \
            .group_by(Article.user_id).all()
        return ret
