from flask_restful import Resource, abort
from flask import g, current_app
from sqlalchemy.orm import load_only
from flask_restful.reqparse import RequestParser
from flask_restful import inputs
import re
import random
from datetime import datetime
import time
from redis.exceptions import ConnectionError
from sqlalchemy.exc import SQLAlchemyError

from models.news import Article, ArticleContent, Attitude
from rpc.recommend import user_reco_pb2, user_reco_pb2_grpc
from . import constants
from utils import parser
from cache import article as cache_article
from cache import user as cache_user
from cache import statistic as cache_statistic
from models import db
from utils.decorators import login_required, validate_token_if_using, set_db_to_write, set_db_to_read
from utils.logging import write_trace_log


class ArticleResource(Resource):
    """
    文章
    """
    method_decorators = [set_db_to_read, validate_token_if_using]

    def _feed_similar_articles(self, article_id):
        """
        获取相似文章
        :param article_id:
        :return:
        """
        req = user_reco_pb2.Article()
        req.article_id = article_id
        req.article_num = constants.RECOMMENDED_SIMILAR_ARTICLE_MAX

        stub = user_reco_pb2_grpc.UserRecommendStub(current_app.rpc_reco)
        resp = stub.article_recommend(req)

        return resp.article_id

    def get(self, article_id):
        """
        获取文章详情
        :param article_id: int 文章id
        """
        # 写入埋点日志
        qs_parser = RequestParser()
        qs_parser.add_argument('Trace', type=inputs.regex(r'^.+$'), required=False, location='headers')
        args = qs_parser.parse_args()

        user_id = g.user_id

        # 查询文章数据
        exist = cache_article.ArticleInfoCache(article_id).exists()
        if not exist:
            abort(404, message='The article does not exist.')

        article = cache_article.ArticleDetailCache(article_id).get()

        # 推荐系统所需埋点
        if args.Trace:
            write_trace_log(args.Trace, channel_id=article['ch_id'])

        article['is_followed'] = False
        article['attitude'] = None

        if user_id:
            # 非匿名用户添加用户的阅读历史
            try:
                cache_user.UserReadingHistoryStorage(user_id).save(article_id)
            except ConnectionError as e:
                current_app.logger.error(e)

            # 查询关注
            article['is_followed'] = cache_user.UserFollowingCache(user_id).determine_follows_target(article['aut_id'])

            # 查询登录用户对文章的态度（点赞or不喜欢）
            try:
                article['attitude'] = cache_article.ArticleUserAttitudeCache(user_id, article_id).get()
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                article['attitude'] = -1

        # 获取相关文章推荐
        article['recomments'] = []
        try:
            similar_articles = self._feed_similar_articles(article_id)
            for _article_id in similar_articles:
                _article = cache_article.ArticleInfoCache(_article_id).get()
                article['recomments'].append({
                    'art_id': _article['art_id'],
                    'title': _article['title']
                })
        except Exception as e:
            current_app.logger.error(e)

        # 更新阅读数
        cache_statistic.ArticleReadingCountStorage.incr(article_id)
        cache_statistic.UserArticlesReadingCountStorage.incr(article['aut_id'])

        return article


class ArticleListResource(Resource):
    """
    获取推荐文章列表数据
    """
    method_decorators = [set_db_to_read, validate_token_if_using]

    # def _get_recommended_articles(self, channel_id, page, per_page):
    #     """
    #     获取推荐的文章（伪推荐）已废弃
    #     :param channel_id: 频道id
    #     :param page: 页数
    #     :param per_page: 每页数量
    #     :return: [article_id, ...]
    #     """
    #     offset = (page - 1) * per_page
    #     articles = Article.query.options(load_only()).filter_by(channel_id=channel_id, status=Article.STATUS.APPROVED)\
    #         .order_by(Article.id).offset(offset).limit(per_page).all()
    #     if articles:
    #         return [article.id for article in articles]
    #     else:
    #         return []

    def _feed_articles(self, channel_id, feed_count):
        """
        获取推荐文章
        :param channel_id: 频道id
        :param feed_count: 推荐数量
        :return: [{article_id, trace_params}, ...]
        """
        req = user_reco_pb2.User()

        if g.user_id:
            req.user_id = str(g.user_id)
        elif g.anonymous_id:
            req.user_id = str(g.anonymous_id)
        else:
            req.user_id = ''

        req.channel_id = channel_id
        req.article_num = feed_count

        stub = user_reco_pb2_grpc.UserRecommendStub(current_app.rpc_reco)
        resp = stub.user_recommend(req)

        # 曝光埋点参数
        trace_exposure = resp.exposure
        write_trace_log(trace_exposure, channel_id=channel_id)

        return resp.recommends

    # def _generate_article_cover(self, article_id):
    #     """
    #     生成文章封面(处理测试数据专用） 已废弃
    #     :param article_id: 文章id
    #     """
    #     article = Article.query.options(load_only(Article.cover)).filter_by(id=article_id).first()
    #     if article.cover['type'] > 0:
    #         return
    #     content = ArticleContent.query.filter_by(id=article_id).first()
    #     if content is None:
    #         return
    #     results = re.findall(r'src=\"http([^"]+)\"', content.content)
    #     length = len(results)
    #     if length <= 0:
    #         return
    #     elif length < 3:
    #         img_url = random.choice(results)
    #         img_url = 'http' + img_url
    #         Article.query.filter_by(id=article_id).update({'cover': {'type': 1, 'images': [img_url]}})
    #         db.session.commit()
    #     else:
    #         random.shuffle(results)
    #         img_urls = results[:3]
    #         img_urls = ['http'+img_url for img_url in img_urls]
    #         Article.query.filter_by(id=article_id).update({'cover': {'type': 3, 'images': img_urls}})
    #         db.session.commit()

    def get(self):
        """
        获取文章列表
        /v1_0/articles?channel_id&page&per_page
        """
        qs_parser = RequestParser()
        qs_parser.add_argument('channel_id', type=parser.channel_id, required=True, location='args')
        qs_parser.add_argument('page', type=inputs.positive, required=False, location='args')
        qs_parser.add_argument('per_page', type=inputs.int_range(constants.DEFAULT_ARTICLE_PER_PAGE_MIN,
                                                                 constants.DEFAULT_ARTICLE_PER_PAGE_MAX,
                                                                 'per_page'),
                               required=False, location='args')
        args = qs_parser.parse_args()
        channel_id = args.channel_id
        page = 1 if args.page is None else args.page
        per_page = args.per_page if args.per_page else constants.DEFAULT_ARTICLE_PER_PAGE_MIN

        results = []

        if page == 1:
            # 第一页
            top_article_id_li = cache_article.ChannelTopArticlesStorage(channel_id).get()
            for article_id in top_article_id_li:
                article = cache_article.ArticleInfoCache(article_id).get()
                if article:
                    results.append(article)

        # 获取推荐文章列表
        # ret = self._get_recommended_articles(channel_id, page, per_page)
        # feed推荐 未使用page参数
        feeds = self._feed_articles(channel_id, per_page)

        # 查询文章
        for feed in feeds:
            # self._generate_article_cover(article_id)
            article = cache_article.ArticleInfoCache(feed.article_id).get()
            if article:
                article['trace'] = {
                    'click': feed.params.click,
                    'collect': feed.params.collect,
                    'share': feed.params.share,
                    'read': feed.params.read
                }
                results.append(article)

        return {'page': page, 'per_page': per_page, 'results': results}


class ArticleListResourceV1D1(Resource):
    """
    获取推荐文章列表数据
    """
    method_decorators = [set_db_to_read, validate_token_if_using]

    def _feed_articles(self, channel_id, timestamp, feed_count):
        """
        获取推荐文章
        :param channel_id: 频道id
        :param feed_count: 推荐数量
        :param timestamp: 时间戳
        :return: [{article_id, trace_params}, ...], timestamp
        """
        req = user_reco_pb2.User()

        if g.user_id:
            req.user_id = str(g.user_id)
        elif g.anonymous_id:
            req.user_id = str(g.anonymous_id)
        else:
            req.user_id = ''

        req.channel_id = channel_id
        req.article_num = feed_count
        req.time_stamp = timestamp

        stub = user_reco_pb2_grpc.UserRecommendStub(current_app.rpc_reco)
        try:
            resp = stub.user_recommend(req, timeout=5)
        except Exception as e:
            current_app.logger.error(e)
            return [], timestamp

        # 曝光埋点参数
        trace_exposure = resp.exposure
        if len(resp.recommends) > 0 and trace_exposure:
            write_trace_log(trace_exposure, channel_id=channel_id)

        return resp.recommends, resp.time_stamp

    def get(self):
        """
        获取文章列表
        /v1_1/articles?channel_id&timestamp
        """
        qs_parser = RequestParser()
        qs_parser.add_argument('channel_id', type=parser.channel_id, required=True, location='args')
        qs_parser.add_argument('timestamp', type=inputs.positive, required=True, location='args')
        qs_parser.add_argument('with_top', type=inputs.boolean, required=True, location='args')
        args = qs_parser.parse_args()
        channel_id = args.channel_id
        timestamp = args.timestamp
        with_top = args.with_top
        per_page = constants.DEFAULT_ARTICLE_PER_PAGE_MIN
        try:
            feed_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(timestamp/1000))
        except Exception:
            return {'message': 'timestamp param error'}, 400

        results = []
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        if with_top:
            # 包含置顶
            top_article_id_li = cache_article.ChannelTopArticlesStorage(channel_id).get()
            for article_id in top_article_id_li:
                article = cache_article.ArticleInfoCache(article_id).get()
                if article:
                    article['pubdate'] = now
                    results.append(article)

        # 获取推荐文章列表
        feeds, pre_timestamp = self._feed_articles(channel_id, timestamp, per_page)

        # 查询文章
        for feed in feeds:
            article = cache_article.ArticleInfoCache(feed.article_id).get()
            if article:
                article['pubdate'] = feed_time
                article['trace'] = {
                    'click': feed.params.click,
                    'collect': feed.params.collect,
                    'share': feed.params.share,
                    'read': feed.params.read
                }
                results.append(article)

        return {'pre_timestamp': pre_timestamp, 'results': results}


class UserArticleListResource(Resource):
    """
    用户文章列表
    """
    method_decorators = [set_db_to_read]

    def get(self, user_id):
        """
        获取user_id 用户的文章数据
        """
        exist = cache_user.UserProfileCache(user_id).exists()
        if not exist:
            return {'message': 'Invalid request.'}, 400
        qs_parser = RequestParser()
        qs_parser.add_argument('page', type=inputs.positive, required=False, location='args')
        qs_parser.add_argument('per_page', type=inputs.int_range(constants.DEFAULT_ARTICLE_PER_PAGE_MIN,
                                                                 constants.DEFAULT_ARTICLE_PER_PAGE_MAX,
                                                                 'per_page'),
                               required=False, location='args')
        args = qs_parser.parse_args()
        page = 1 if args.page is None else args.page
        per_page = args.per_page if args.per_page else constants.DEFAULT_ARTICLE_PER_PAGE_MIN

        results = []

        # 已废弃
        # articles = cache_user.get_user_articles(user_id)
        # total_count = len(articles)
        # page_articles = articles[(page - 1) * per_page:page * per_page]

        total_count, page_articles = cache_user.UserArticlesCache(user_id).get_page(page, per_page)

        for article_id in page_articles:
            article = cache_article.ArticleInfoCache(article_id).get()
            if article:
                results.append(article)

        return {'total_count': total_count, 'page': page, 'per_page': per_page, 'results': results}


class CurrentUserArticleListResource(Resource):
    """
    当前用户的文章列表
    """
    method_decorators = [set_db_to_read, login_required]

    def get(self):
        """
        获取当前用户的文章列表
        """
        qs_parser = RequestParser()
        qs_parser.add_argument('page', type=inputs.positive, required=False, location='args')
        qs_parser.add_argument('per_page', type=inputs.int_range(constants.DEFAULT_ARTICLE_PER_PAGE_MIN,
                                                                 constants.DEFAULT_ARTICLE_PER_PAGE_MAX,
                                                                 'per_page'),
                               required=False, location='args')
        args = qs_parser.parse_args()
        page = 1 if args.page is None else args.page
        per_page = args.per_page if args.per_page else constants.DEFAULT_ARTICLE_PER_PAGE_MIN

        results = []

        # 已废弃
        # articles = cache_user.get_user_articles(g.user_id)
        # total_count = len(articles)
        # page_articles = articles[(page - 1) * per_page:page * per_page]

        total_count, page_articles = cache_user.UserArticlesCache(g.user_id).get_page(page, per_page)

        for article_id in page_articles:
            article = cache_article.ArticleInfoCache(article_id).get()
            if article:
                results.append(article)

        return {'total_count': total_count, 'page': page, 'per_page': per_page, 'results': results}

