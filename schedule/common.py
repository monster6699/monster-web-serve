from toutiao import create_flask_app
from settings.default import DefaultConfig


flask_app = create_flask_app(DefaultConfig, enable_config_file=True)

from redis.sentinel import Sentinel
_sentinel = Sentinel(flask_app.config['REDIS_SENTINELS'])
redis_master = _sentinel.master_for(flask_app.config['REDIS_SENTINEL_SERVICE_NAME'])

from models import db

db.init_app(flask_app)
