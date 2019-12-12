# coding=utf-8
# python3


from werkzeug.middleware.profiler import ProfilerMiddleware
from app import create_app

app = create_app(config_name="development")

if __name__ == "__main__":
    # app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[20])
    app.run(host="0.0.0.0", port=5000)

