import main
from urllib.parse import parse_qsl,unquote
import ujson as js

def application(env, start_response):
    # /api/signup?a=b -> '','api','signup?a=b' => 'signup', 'a=b'
    parts = env['REQUEST_URI'].split('/')[2].split('?')
    # Cuts up the REQUEST_URI (after the ip address)
    mode=env['REQUEST_METHOD'] #HTTP Methods such as GET,POST,etc
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
                data |= js.loads(nd)
            elif mode == 'PUT':
                data |= dict([(k.decode('utf-8'),v.decode('utf-8')) for k,v in parse_qsl(nd)])
        except Exception as e:
            print('ALERT: Some sort of data type error in api.py')
            print(e)
            print("This could be bcz of some unimplemented POST or PUT method")
    elif len(parts) == 2:
        data |= parse_qsl(unquote(parts[1]))
    data['ip'] = env['REMOTE_ADDR']
    # give mode,operation (AKA endpoint),data,and function to reply
    return main.run(mode,parts[0],data,start_response)
