import json

def application(env, start_response):
    print(env["REQUEST_METHOD"])
    if 'HTTP_DATA' in env:
        print(json.loads(env["HTTP_DATA"]))
    start_response('200 OK', [('Content-Type', 'text/plain;charset=utf-8')])
    return [b'Hello World!\n']
