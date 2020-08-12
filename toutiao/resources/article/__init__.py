from flask import Blueprint
from flask_restful import Api

from . import upload, categories, cover
from utils.output import output_json

actilce_bp = Blueprint('articles', __name__)
acticle_api = Api(actilce_bp, catch_all_404s=True)
acticle_api.representation('application/json')(output_json)

acticle_api.add_resource(upload.ArticleCreateResourece, '/article/create', endpoint='ArticleCreateResourece')
acticle_api.add_resource(categories.GetCatergoryResourece, '/article/catergoy/list', endpoint='GetCatergoryResourece')
acticle_api.add_resource(cover.ArticleCoverListResourece, '/article/cover/list', endpoint='ArticleCoverListResourece')
