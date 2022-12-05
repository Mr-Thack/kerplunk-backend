import main
import urllib.parse
import ujson as js

def application(env, start_response):
    # /api/signup?a=b -> '','api','signup?a=b' => 'signup', 'a=b'
    parts = env['REQUEST_URI'].split('/')[2].split('?')
    # Cuts up the REQUEST_URI (after the ip address)
    mode=env['REQUEST_METHOD'] #HTTP Methods such as GET,POST,etc
    data = []
    if env.get('CONTENT_LENGTH'):
        # wsgi.input and content_len will come as a char array
        # convertFromJSON(HTTPBody.toString.substring(lengthOfHTTPBody))
        try:
            data.extend(js.loads(env['wsgi.input'].read(int(env['CONTENT_LENGTH']))).items())
        except Exception as e:
            print('api.py:17')
            print(e)
    else:
        data = urllib.parse.parse_qsl(parts[1])
    data.extend([('ip',env['REMOTE_ADDR'])])
    # give mode,operation (AKA endpoint),data,and function to reply
    return main.run(mode,parts[0],dict(data),start_response)
