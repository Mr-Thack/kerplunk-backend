# kerplunk-backend
The backend for Kerplunk, written in Python ASGI.
It'll probably run under Lighttpd
Also, note that this requires atleast Python 3.9

# More Documentation:
Run the server, then go to http://localhost:8000/docs

# Alert(s):
We're using FastAPI, read their documentation!
For sockets, we're using FastAPI which uses Starlette.
Read their documentation! (Only for websockets!)

We're using OAuth for authentication.

We're using orjson instead of the std library's json implementation,
because orjson is leagues ahead in speed!
Might complain when installing using pip.
https://github.com/ijl/orjson#questions

# Install Required Packages
```
pip install -r requirements.txt
```

# Run for Debug
```
cd api
uvicorn main:app
```

# Run for Deployment 
```
cd api
gunicorn main:app --worker 4 --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8080

# 4 worker (optional), on Uvicorn (required), 0.0.0.0 (global addresses),
:8080, (port 8080 because that's how I set up iptables)
```
# Automatically Test API Using Unittest
```
cd api
python3 unit_tests.py
```
Write more tests when new features are added!

# How to Access LMDB
Our custom wrapper is in dblib.py. It does the hard work for us!
1. Opening a DB
```
from dblib import db
from dataclasses import dataclass


@dataclass
class User():
    id: str
    username: str
    logins: int = 0
    realname: str | None = None


users: db = db('FileName', schema)  # Set up DB with schema
users[0] = User('br18tb@ck', 'not_dead_yet')  # Initialize a new user
users[0, 'logins'] = 1  # Set logins of user 0 to 1
del users[1]  # remove him from db
"""
That's it!
dblib.py wraps around LMDB almost like a dictionary from the standard library!
Of course you'll need to know type hintings, but those aren't hard!
"""
```

# Warning
## Only Somewhat Tested! Probably will Crash!##
But it'll restart itself on crash, so no worries!
