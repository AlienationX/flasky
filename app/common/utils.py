# coding=utf-8
# python3

import arrow


class Utils:

    @staticmethod
    def to_utc(dt):
        """
        :param dt:
        :return datetime:
        """
        return arrow.get(dt, "Asia/Shanghai").to("utc")

    @staticmethod
    def test():
        print("testing...")
