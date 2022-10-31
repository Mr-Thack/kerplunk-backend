import ujson as js
import operations
import cython

switch : dict
op : tuple

def send(OPERATION: cython.char[16], MODE: cython.char[8], DATA: str, resp):
    switch = {
        'GET' : 0,
        'POST' : 1,
        'PUT' : 2,
        'DELETE' : 3
    }
    try:
        op = operations.opFuncs[operations.opNames.index(OPERATION)][switch.get(MODE,5)]
    except:
        resp('402 NONEXISTANT OPERATION',[('Content-Type','text/plain;charset=utf-8')])
        return ''
    return op(DATA,resp)

#TODO, the error codes are wrong, set them to correct HTTP error codes
#environ, respond
def run(env,resp):
    print("Someone's coming from " + env['REMOTE_ADDR'])
    OPERATION: cython.char[16]
    opindx : cython.int
    fnindx : cython.int
    reqsize : cython.int
    HTTP_DATA : str
    REQBODY : str
    MODE : cython.char[8]
    # /api/signup -> '','api','signup'
    OPERATION = env['REQUEST_URI'].split("/")[2]
    MODE = env['REQUEST_METHOD']
    if 'HTTP_DATA' in env or int(env['CONTENT_LENGTH']) > 0 or MODE == 'GET':
        try:
            DATA = js.loads(env['HTTP_DATA'])
        except:
            try:
                DATA = js.loads(str(env['wsgi.input'].read(int(env['CONTENT_LENGTH'])),'UTF-8'))
            except:
                DATA = ''
        return bytes(send(OPERATION,MODE,DATA,resp),'ASCII')
    else:
        resp('401 NO DATA', [('Content-Type', 'text/plain;charset=utf-8')])
        return [b'']
    # Now we only need to check for operation
    if OPERATION is None:
        resp('400 NO SPECIFIED OPERATION', [('Content-Type','text/plain;charset=utf-8')])
        return [b'']

