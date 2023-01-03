from operations import opFuncs, opNames

MODES = dict(zip(['GET', 'POST', 'PUT', 'DELETE'], range(4)))
# ENUM for HTTP Modes


def send(op: str, mode: str, DATA: dict, resp):
    if str(op) in opNames and str(mode) in MODES:
        return opFuncs[opNames.index(op)][MODES[mode]](DATA, resp)
    # handlerFunctions[nameOfHanderFuncUserWants][ModeOfUser](DATA,resp)
    else:
        print('Endpoint ' + op + ' on mode ' + mode + ' not found')
        resp('404', [('Content-Type', 'text/plain;charset=utf-8')])
        return [b' ']


# TODO, the error codes are wrong, set them to correct HTTP error codes
# environ, respond
def run(mode, operation, data, resp):
    if data != '' or mode == 'GET' or mode == 'POST':
        # If there's no data or on GET
        return send(operation, mode, data, resp)
        # return array of bytes of response
    else:
        resp('401', [('Content-Type', 'text/plain;charset=utf-8')])
        return [b' ']
    # Now we only need to check for operation
    if operation is None:
        resp('400', [('Content-Type', 'text/plain;charset=utf-8')])
        return [b' ']
