import os

from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from werkzeug.datastructures import FileStorage
from fdfs_client.client import Fdfs_client, get_tracker_conf
from werkzeug.utils import secure_filename

from utils.decorators import set_db_to_write, login_required


class UploadImageResource(Resource):
    """
    修改用户信息
    """

    method_decorators = [login_required]

    def post(self):
        json_parser = RequestParser()
        json_parser.add_argument('files', type=FileStorage, required=True, location='files')
        args = json_parser.parse_args()
        content = self._uploag_fastdfs(args.files)
        return {"file_path": content}

    def _uploag_fastdfs(self, files):
        current_path = os.path.split(os.path.realpath(__file__))[0]
        config_path = os.path.join(current_path, "client.conf")
        tracker_path = get_tracker_conf(config_path)
        client = Fdfs_client(tracker_path)
        ret_upload = client.upload_by_buffer(files.read(), file_ext_name="png")
        file_path = ret_upload['Remote file_id'].decode()
        return file_path
