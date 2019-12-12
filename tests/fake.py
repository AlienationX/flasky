# coding=utf-8
# python3

from faker import Faker
from random import randint
from mysql.connector import connect
import hashlib
import arrow
import random

conn = connect(host="127.0.0.1", port=3306, user="root", password="root", db="flasky")
cursor = conn.cursor()


def create_fake(language=None):
    # language = "zh_CN"
    if language:
        fake = Faker(language)
    else:
        fake = Faker()
    return fake


def create_datetime(start_date="2019-01-01 00:00:00", end_date=arrow.now().format("YYYY-MM-DD HH:mm:ss")):
    seconds = 60 * 60 * 24
    days = 0


def generate_users(count=100, language=None):
    fake = create_fake(language)
    for i in range(count):
        password = "password"
        email = fake.email()
        users_sql = """insert into users (
                   username,
                   password,
                   password_hash,
                   email,
                   email_hash,
                   real_name,
                   gender,
                   birthday,
                   location,
                   address,
                   about_me,
                   create_time
                ) values (
                   '{username}',
                   '{password}',
                   '{password_hash}',
                   '{email}',
                   '{email_hash}',
                   '{real_name}',
                   '{gender}',
                   '{birthday}',
                   '{location}',
                   '{address}',
                   '{about_me}',
                   '{create_time}'
                )""".format(
            username=fake.user_name(),
            password=password,
            password_hash=hashlib.md5(password.encode("utf-8")).hexdigest(),
            email=email,
            email_hash=hashlib.md5(email.encode("utf-8")).hexdigest(),
            real_name=fake.name(),
            gender=fake.profile()["sex"],
            birthday=fake.date_of_birth(),
            location=fake.city(),
            address=fake.address(),
            about_me=fake.text()[:32],
            create_time=(fake.date_time_between_dates(arrow.get("2019-01-01").datetime, arrow.now().datetime)).strftime("%Y-%m-%d %H:%M:%S")
        )
        # print(users_sql)
        cursor.execute(users_sql)
        try:
            conn.commit()
        except:
            conn.rollback()


def generate_posts(count=100, language=None):
    fake = create_fake(language)
    cursor.execute("select id from users")
    user_ids = [x[0] for x in cursor.fetchall()]
    user_count = len(user_ids)
    for i in range(count):
        posts_sql = "insert into posts (body,create_time,author_id) values ('{body}','{create_time}',{author_id})".format(
            body=fake.text()[:140],
            create_time=fake.date_time_between_dates(arrow.get("2019-06-15").datetime, arrow.now().datetime).strftime("%Y-%m-%d %H:%M:%S"),
            author_id=user_ids[randint(0, user_count - 1)]
        )
        # print(posts_sql)
        cursor.execute(posts_sql)
        if i == count - 1 or i % 1000 == 0:
            conn.commit()


def generate_follows(count=500):
    fake = create_fake()
    cursor.execute("select id from users")
    user_ids = [x[0] for x in cursor.fetchall()]
    user_count = len(user_ids)
    for i in range(count):
        follows_sql = "insert into follows (follower_id,followed_id,create_time) values ({follower_id},{followed_id},'{create_time}')".format(
            follower_id=user_ids[randint(0, user_count - 1)],
            followed_id=user_ids[randint(0, user_count - 1)],
            create_time=fake.date_time_between_dates(arrow.get("2019-06-15").datetime, arrow.now().datetime).strftime("%Y-%m-%d %H:%M:%S")
        )
        try:
            cursor.execute(follows_sql)
            conn.commit()
            print("commit {}".format(str(i)))
        except Exception as e:
            print("rollback {} {}".format(str(i), str(e)))
            conn.rollback()


if __name__ == "__main__":
    # generate_users(language="zh_CN")
    generate_posts(count=100000, language="zh_CN")
    # generate_follows()
    cursor.close()
    conn.close()
