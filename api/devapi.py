#!/usr/bin/python3
from http.server import CGIHTTPRequestHandler, HTTPServer
import sys
import api

# So, basically, I'm too lazy to
# go implement an actual Python server
# just for devtesting,
# so this file mimics SCGI just enough
# to convince api.py into working

class MyServer(CGIHTTPRequestHandler):
    def respond(self,code,headers):
        self.send_response(int(code))
        for h in headers: # respond to request
            self.send_header(h[0],h[1])
        self.end_headers()
    def do_GET(self):
        if self.path == '/favicon.ico': # Too much work to send one
            self.respond('200',[('Content-Type','text/plain;charset=utf8')])
            self.wfile.write(bytes('','utf8'))
            return ''
        env = { # All we need for SCGI Interface
            'REQUEST_URI':self.path,
            'REQUEST_METHOD':self.command,
            'REMOTE_ADDR':self.client_address[0]
        } # We model everything off SCGI because this script tries to imitate SCGI
        for r in api.application(env,self.respond): #give data in env, and ability to respond
            self.wfile.write(r) # Send data back to dev
    def do_POST(self):
        env = { # Data for SCGI Interface POST
            'REQUEST_URI':self.path,
            'REQUEST_METHOD':self.command,
            'REMOTE_ADDR':self.client_address[0],
            'CONTENT_LENGTH':self.headers['Content-Length'],
            'wsgi.input':self.rfile
        } # We model everything off SCGI because this script tries to imitate SCGI
        #print(self.rfile.read(int(self.headers['Content-Length'])))
        for r in api.application(env,self.respond):
            self.wfile.write(r)

def main():
    hostName = "127.0.0.1"
    serverPort = 8080
    print('Using below as bind address (specify 127.0.0.1 as first argument to program for local testing)')
    try:
        hostName = sys.argv[1] # Try to see if hostname specified
    except:
        print("No hostname given, defaulting to 127.0.0.1")
    try:
        serverPort = int(sys.argv[2]) # Try to see if port specified
    except:
        print("No port give, defaulting to 8080")
    print("Server started http://%s:%s" % (hostName, serverPort))
    webServer = HTTPServer((hostName, serverPort), MyServer)
    # Stat a HTTP Python Web server
    try:
        webServer.serve_forever()
        # respawns even on crash
    except KeyboardInterrupt:
        # For example, CTRL+C
        pass
    webServer.server_close() # Shutup and stop
    print("Server stopped.")

if __name__=='__main__':
    main()
