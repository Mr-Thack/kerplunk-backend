from uvicorn_main import main
from urllib.parse import parse_qsl,unquote
from orjson import loads as loadjson
from uvicorn import Config, Server

async def read_body(receive):
    """
    Read and return the entire body from an incoming ASGI message.
    """
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body

async def application(scope, recieved, send):
    assert scope['type'] == 'http' # We don't handle HTTPS??
    mode=env['method'] #HTTP Methods such as GET,POST,etc
    data : dict = {}
    if env.get('CONTENT_LENGTH') and env['CONTENT_LENGTH']!='0':
        # wsgi.input and content_len will come as a char array
        # convertFromJSON(HTTPBody.toString.substring(lengthOfHTTPBody))
        nd = env['wsgi.input'].read(int(env['CONTENT_LENGTH']))
        try:
            # Note that this does not support FORM data
            # We are only accepting post data as JSON & Query???
            # TODO: add support for POSTing in FORM, which might be the same as Query
            if mode=='POST':
                data |= loadjson(nd)
            elif mode == 'PUT':
                data |= dict([(k.decode('utf-8'),v.decode('utf-8')) for k,v in parse_qsl(nd)])
        except Exception as e:
            print('ALERT: Some sort of data type error in api.py')
            print(e)
            print("This could be bcz of some unimplemented POST or PUT method")
    elif env['QUERY_STRING']:
        data |= parse_qsl(unquote(env['QUERY_STRING']))#parse_qsl(unquote(parts[1]))
    data['ip'] = env['REMOTE_ADDR']
    # We remove the first 5 characters (/api/Endpoint) => Endpoint
    # give mode,operation (AKA endpoint),data,and function to reply
    return main.run(mode,env['PATH_INFO'][5:],data,start_response)

def run():
    config = Config('api_uvicorn:application',port=8000, log_level='info')
    server = Server(config)
    server.run()
