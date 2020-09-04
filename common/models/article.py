from datetime import datetime

from . import db


class Category(db.Model):
    """
    博客分类
    """
    __tablename__ = 'blog_category'

    class STATUS:
        ENABLE = 1
        DISABLE = 0

    id = db.Column(db.Integer, primary_key=True, doc='分类ID')
    name = db.Column('name', db.String, doc='分类名称')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')
    status = db.Column(db.Integer, default=1, doc='状态')


class Cover(db.Model):
    """
    博客封面
    """
    __tablename__ = 'blog_cover'

    class STATUS:
        ENABLE = 1
        DISABLE = 0

    id = db.Column('id', db.Integer, primary_key=True, doc='封面ID')
    title = db.Column('title', db.String, doc='标题')
    image = db.Column('image', db.String, doc="图片地址")
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')
    status = db.Column(db.Integer, default=1, doc='状态')


class Content(db.Model):
    """
    博客内容
    """
    __tablename__ = 'blog_content'

    id = db.Column('id', db.Integer, primary_key=True, doc='ID')
    title = db.Column(db.String, doc='标题')
    content = db.Column(db.String, doc='内容')
    category_id = db.Column(db.Integer, db.ForeignKey('blog_category.id'), doc='分类id')
    category = db.relationship('Category', uselist=False)
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')
    status = db.Column(db.Integer, default=1, doc='状态')


