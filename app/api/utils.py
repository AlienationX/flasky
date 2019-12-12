# coding=utf-8
# python3

import datetime
import arrow


class UtilityCommon:
    pass


class UtilityDatetime:

    @classmethod
    def format_datetime(cls, input_dt):
        if input_dt is None:
            return ""
        a = arrow.get(input_dt)
        dt_str = a.format("YYYY-MM-DD HH:mm:ss")
        return dt_str


if __name__ == "__main__":
    now = datetime.datetime.now()
    print(UtilityDatetime.format_datetime(now))
