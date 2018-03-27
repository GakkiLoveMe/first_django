from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FdfsStorage(Storage):
    """自定义文件存储类"""
    def __init__(self):
        self.client = settings.FDFS_CLIENT
        self.server = settings.FDFS_SERVER

    def save(self, name, content, max_length=None):
        # 读取文件数据
        content = content.read()

        # 创建fdfs服务器客户端,制定tracker服务器
        client = Fdfs_client(settings.FDFS_CLIENT)

        # fdfs服务器存储文件
        try:
            result = client.upload_appender_by_buffer(content)
        except:
            raise

        # 数据库存储路径
        """{'Local file name': '', 'Uploaded size': '165.00KB', 'Group name': 'group1',
            'Storage IP': '192.168.128.132', 'Status': 'Upload successed.',
            'Remote file_id': 'group1/M00/00/00/wKiAhFq4vN6EKKihAAAAAAJo_yQ6044689'}
        """
        if result.get('Status') == "Upload successed.":
            return result.get('Remote file_id')
        else:
            raise Exception('上传文件失败!')

    def url(self, name):
        """添加属性返回图片的地址"""
        # return 'http//:127.0.0.1:8888' + name
        return self.server + name


