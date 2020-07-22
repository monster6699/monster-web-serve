from flask import Blueprint
from flask_restful import Api

from . import article, collection, liking, dislike, report, comment, channel, reading
from utils.output import output_json


admin_bp = Blueprint('admin', __name__)
admin_api = Api(admin_bp, catch_all_404s=True)
admin_api.representation('application/json')(output_json)


admin_api.add_resource(article.ArticleResource, '/admin/user/list',
                      endpoint='Article')

# news_api.add_resource(article.ArticleListResource, '/v1_0/articles',
#                       endpoint='Articles')

admin_api.add_resource(article.ArticleListResourceV1D1, '/v1_1/articles',
                      endpoint='ArticlesV1_1')
