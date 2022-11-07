from http.server import CGIHTTPRequestHandler, HTTPServer
import sys
import api

hostName = "127.0.0.1"
serverPort = 8080
# So, basically, I'm too lazy to
# go implement an actual Python server
# just for devtesting,
# so this file mimics SCGI just enough
# to convince api.py into working

class MyServer(CGIHTTPRequestHandler):
    def respond(self,code,headers):
        self.send_response(int(code))
        for h in headers:
            self.send_header(h[0],h[1])
        self.end_headers()
    def do_GET(self):
        if self.path == '/favicon.ico':
            self.respond('200',[('Content-Type','text/plain;charset=utf8')])
            self.wfile.write(bytes('','utf8'))
            return ''
        env = {
            'REQUEST_URI':self.path,
            'REQUEST_METHOD':self.command,
            'REMOTE_ADDR':self.client_address[0]
        } # We model everything off SCGI because this script tries to imitate SCGI
        for r in api.application(env,self.respond):
            self.wfile.write(r)
    def do_POST(self):
        env = {
            'REQUEST_URI':self.path,
            'REQUEST_METHOD':self.command,
            'REMOTE_ADDR':self.client_address[0],
            'CONTENT_LENGTH':self.headers['Content-Length'],
            'wsgi.input':self.rfile
        } # We model everything off SCGI because this script tries to imitate SCGI
        for r in api.application(env,self.respond):
            self.wfile.write(r)

if __name__ == "__main__":
    print('Using below as bind address (specify 127.0.0.1 as first argument to program for local testing)')
    try:
        hostName = sys.argv[1]
    except:
        print("No hostname given, defaulting to 127.0.0.1")
    try:
        serverPort = int(sys.argv[2])
    except:
        print("No port give, defaulting to 8080")
    print("Server started http://%s:%s" % (hostName, serverPort))
    webServer = HTTPServer((hostName, serverPort), MyServer)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
