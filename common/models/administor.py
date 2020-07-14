from datetime import datetime

from models import db


class Administrator(db.Model):
    """
    管理员基本信息
    """
    __tablename__ = 'admin_user'

    class STATUS:
        ENABLE = 1
        DISABLE = 0

    id = db.Column(db.Integer, primary_key=True, doc='管理员ID')
    username = db.Column(db.String, doc='账号')
    password = db.Column(db.String, doc='密码')
    name = db.Column(db.String, doc='管理员名称')
    email = db.Column(db.String, doc='电子邮箱')
    mobile = db.Column(db.String, doc='手机号')
    status = db.Column(db.Integer, default=1, doc='状态')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')


class AdministratorRole(db.Model):
    """
    管理员组/角色
    """
    __tablename__ = 'admin_role'

    class STATUS:
        ENABLE = 1
        DISABLE = 0

    id = db.Column(db.Integer, primary_key=True, doc='管理员角色/组ID')
    name = db.Column(db.String, doc='角色/组')
    status = db.Column(db.Integer, default=1, doc='状态')
    remark = db.Column(db.String, doc='备注')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')


class AdministratorMenu(db.Model):
    """
    菜单表
    """
    __tablename__ = 'admin_menu'

    class STATUS:
        ENABLE = 1
        DISABLE = 0

    id = db.Column('id', db.Integer, primary_key=True, doc='菜单ID')
    name = db.Column(db.String, doc='菜单名称')
    path = db.Column(db.String, doc='菜单路径')
    meta = db.Column(db.String, doc='菜单信息')
    menu_order = db.Column(db.Integer, doc='排序')
    remark = db.Column(db.String, doc='备注')
    status = db.Column(db.Integer, default=1, doc='状态')
    parent_id = db.Column(db.Integer, db.ForeignKey('admin_menu.id'), doc='父节点')
    parent = db.relationship('AdministratorMenu', uselist=False)
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')


class AdministratorRoleMenu(db.Model):
    """
    角色菜单中间表
    """
    __tablename__ = 'admin_role_menu'

    class STATUS:
        ENABLE = 1
        DISABLE = 0

    id = db.Column(db.Integer, primary_key=True, doc='角色菜单ID')
    role_id = db.Column(db.Integer, db.ForeignKey('admin_role.id'), doc='角色ID')
    role = db.relationship('AdministratorRole', uselist=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('admin_menu.id'), doc='菜单ID')
    menu = db.relationship('AdministratorMenu', uselist=False)
    remark = db.Column(db.String, doc='备注')
    status = db.Column(db.Integer, default=1, doc='状态')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')


class AdministratorUserRole(db.Model):
    """
    用户角色中间表
    """
    __tablename__ = 'admin_user_role'

    id = db.Column('id', db.Integer, primary_key=True, doc='用户角色ID')
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), doc='管理员ID')
    user = db.relationship("Administrator", uselist=False)
    role_id = db.Column(db.Integer, db.ForeignKey('admin_role.id'), doc='管理员ID')
    role = db.relationship("AdministratorRole", uselist=False)
    status = db.Column(db.Integer, default=1, doc='状态')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')