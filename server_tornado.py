# coding=utf-8
# python3

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app import create_app

if __name__ == "__main__":
    app = create_app()
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)  # flask默认的端口
    IOLoop.instance().start()
