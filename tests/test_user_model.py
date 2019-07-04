# coding=utf-8
# python3

from app.models import User
import unittest


class UserModelTestCast(unittest.TestCase):

    def test_user_role(self):
        u = User("test@flasky.com")
        # self.assertTrue(u.can(Permission.FOLLOW))
        # self.assertTrue(u.can(Permission.COMMENT))
        # self.assertTrue(u.can(Permission.WRITE))
        # self.assertTrue(u.can(Permission.MODERATE))
        # self.assertTrue(u.can(Permission.ADMIN))

    # def test_anonymous_user(self):
    #     u = AnonymousUser()
    #     self.assertFalse(u.can(Permission.FOLLOW))
    #     self.assertFalse(u.can(Permission.COMMENT))
    #     self.assertFalse(u.can(Permission.WRITE))
    #     self.assertFalse(u.can(Permission.MODERATE))
    #     self.assertFalse(u.can(Permission.ADMIN))
