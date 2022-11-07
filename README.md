# bhalserver-backend
The backend for bhalserver, written in Cython, for FCGI, for Lighttpd

# Required Packages
cython
ujson

# Notes
Any GET request (or any url query parameters) must use `D['field'][0]` becuase of the library we use.
I wish we could use something nicer, but by doing this the library also has support for arrays.

# Warning
As of now, this stuff can't run anywhere, but on the server!
A possible fix to this would be to add a `--dev` switch and then make it listen to a url instead of an SCGI socket
