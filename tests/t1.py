# coding=utf-8
# python3


def func():
    print("Hello World")


class A:
    name = "A"

    def __init__(self):
        self.id = 0
        self.username = "beijing"


if __name__ == '__main__':
    print(A.name)
    print(A().username)
