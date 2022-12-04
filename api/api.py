import main
import urllib.parse
import ujson as js

def application(env, start_response):
    # /api/signup?a=b -> '','api','signup?a=b' => 'signup', 'a=b'
    parts = env['REQUEST_URI'].split('/')[2].split('?')
    # Cuts up the REQUEST_URI (after the ip address)
    data=''
    mode=env['REQUEST_METHOD'] #HTTP Methods such as GET,POST,etc
    if mode=='GET':
        try: # Wrap for error
            data = dict(urllib.parse.parse_qsl(parts[1]))
            # gives an array of tuples
        except:
            pass
    if mode=='POST':
        try:
            # wsgi.input and content_len will come as a char array
            # convertFromJSON(HTTPBody.toString.substring(lengthOfHTTPBody))
            tmp = js.loads(env['wsgi.input'].read(int(env['CONTENT_LENGTH'])))
            print(tmp)
            data = dict([(k, v) for k, v in tmp.items()]) #then convert to array of tuples
        except:
            pass
    # give mode,operation,addr,data
    return main.run(mode,parts[0],env['REMOTE_ADDR'],data,start_response)
