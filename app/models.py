# coding=utf-8
# python3

from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from app import login_manager, db
from app.common.logger import create_logger
import hashlib
import arrow

logger = create_logger(__name__)


class User(UserMixin):
    """必须继承UserMixin，current_user才会默认关联User对象"""
    """修改为不依赖flask_login模块"""

    def __init__(self, user_id=0, username="", email=""):
        self.id = 0
        self.password_hash = ""  # verify_password会用到，提前赋值，同时作为实例化（查询出结果）的判断条件
        self.email_hash = ""
        self.confirmed = False
        sql = "select * from users where id={} or username='{}' or email='{}' limit 1".format(user_id, username, email)
        logger.debug(sql)
        user = db.engine.execute(sql)
        if user.rowcount > 0:
            for row in user:
                for k, v in row.items():
                    setattr(self, k, v)
            # self.email_hash = hashlib.md5(self.email.encode()).hexdigest()
            self.update_login_time()

    @property
    def age(self):
        if hasattr(self, "birthday"):
            return arrow.now().year - arrow.get(self.birthday, "YYYY-MM-DD").year
        return 999

    @property
    def gender_map(self):
        if hasattr(self, "gender"):
            if self.gender == "M":
                gender_f = "男"
            elif self.gender == "F":
                gender_f = "女"
            else:
                gender_f = ""
            return gender_f
        return ""

    # @property
    # def password(self):
    #     raise AttributeError("password is not a readable attribute")

    @staticmethod
    def generate_hash(raw_str):
        """密码加密函数"""
        # salt = "FLASKY"
        # password_format = str(password) + salt
        # return hashlib.md5(password_format.encode()).hexdigest()
        return hashlib.md5(raw_str.encode()).hexdigest()

    def verify_password(self, password):
        """加密密码验证"""
        return self.password_hash == self.generate_hash(password)

    def generate_token(self, expiration=600):
        """根据user_id生成token，expiration为秒"""
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"id": self.id})

    @staticmethod
    def verify_token(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except SignatureExpired:
            # token正确但是过期了
            return False
        except BadSignature:
            # token错误
            return False

        # user = db.engine.execute("select 1 from users t where t.id={} limit 1".format(data.get("id")))
        # if user.rowcount == 0:
        #     return False
        # else:
        #     return True

        if data.get("id") != self.id:
            return False
        else:
            return True

    def update_confirmed(self, token):
        """更新confirmed确认字段"""
        if self.verify_token(token):
            db.session.execute("update users set confirmed=True where id={}".format(self.id))
            db.session.commit()
            self.confirmed = True

    def update_login_time(self):
        """更新已登录用户的最后访问时间"""
        db.session.execute("update users set last_login_time='{}' where id={}".format(arrow.now().format("YYYY-MM-DD HH:mm:ss"), self.id))
        db.session.commit()

    def is_administrator(self):
        return False

    def is_following(self, user_id):
        """是否关注当前用户"""
        sql = "select 1 from follows where follower_id={} and followed_id={}".format(self.id, user_id)
        rows = db.engine.execute(sql)
        return rows.rowcount > 0

    def follow(self, user_id):
        """关注的功能实现"""
        if not self.is_following(user_id):
            sql = "insert into follows (follower_id,followed_id) values ({},{})".format(self.id, user_id)
            db.session.execute(sql)
            db.session.commit

    def unfollow(self, user_id):
        """取消关注的功能实现"""
        if self.is_following(user_id):
            sql = "delete from follows where follower_id={} and followed_id={}".format(self.id, user_id)
            db.session.execute(sql)
            db.session.commit

    def has_follower(self):
        """当前用户的所有关注着"""
        sql = "select 1 as num from follows where follower_id={}".format(self.id)
        rows = db.engine.execute(sql)
        return rows.rowcount

    def has_followed(self):
        """当前用户的所有跟随者（粉丝）"""
        sql = "select 1 as num from follows where followed_id={}".format(self.id)
        rows = db.engine.execute(sql)
        return rows.rowcount

    def has_posts_num(self):
        """当前用户的所有posts"""
        sql = "select count(1) as num from posts where author_id={}".format(self.id)
        num = db.engine.execute(sql).fetchone()[0]
        return num

    def __repr__(self):
        if hasattr(self, "username"):
            return "<User {} {}>".format(self.id, self.username)
        else:
            return "<User 0 anonymous>"


# 该函数很重要，current_user通过该函数赋值
@login_manager.user_loader
def load_user(user_id):
    user = User(user_id=user_id)
    return user
