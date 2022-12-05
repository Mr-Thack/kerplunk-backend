cd api
uwsgi -L --uwsgi-socket 127.0.0.1:3031 --plugin python3 --pythonpath ./ --wsgi-file ./api.py
