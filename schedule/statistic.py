from cache import statistic as cache_statistic

from common import redis_master, flask_app


# 定义关于统计数据计算的任务
def fix_process(statistic_cls):
    """
    通过查询数据库，统计出统计指标的数据，修改redis中保存的记录
    比如，通过查询文章表，计算出每个用户的文章数量，去redis中修改保存的用户文章数记录
    :return:
    """
    # 查询数据库
    with flask_app.app_context():
        ret = statistic_cls.db_query()

    # ret数据的格式
    # [(user_id1, count), (user_id2, count2), (), ()]

    redis_data = []
    for user_id, count in ret:
        redis_data.append(count)  # score
        redis_data.append(user_id)
    # redis_data = [count1, user_id1, count2, user_id2, ...]

    # 修改redis的记录
    # redis中使用的是zset

    # r.zadd(key, count1, use_id1, count2, user_id2)

    statistic_cls.reset(redis_master, *redis_data)


def fix_statistics():
    """
    修正所有需要修正的统计数据
    :return:
    """
    fix_process(cache_statistic.UserArticlesCountStorage)
    fix_process(cache_statistic.ArticleCollectingCountStorage)
    fix_process(cache_statistic.ArticleLikingCountStorage)
