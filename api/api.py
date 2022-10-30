import json
import operations

def application(env, start_response):
    #print(env["REQUEST_METHOD"])
    if 'HTTP_DATA' in env:
        print(json.loads(env["HTTP_DATA"])['operation'])
        start_response('200 OK',[('Content-Type','text/plain;charset=utf-8')])
        return [b"{'rz':'true'}"]
    else:
        start_response('400 NO DATA', [('Content-Type', 'text/plain;charset=utf-8')])
        return [b"{'rz':'false'}"]
