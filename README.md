# bhalserver-backend
The backend for bhalserver, written in Python & Cython, for FCGI, for Lighttpd
We might add a Rust HTTP Server in later
Also, note that this requires atleast Python 3.9
# Install Required Packages
pip install -r requirements.txt

# Run As Server
```
cd api/
python3 testapi.py
```
We could optionally specify ip address and port.
Then go to http://127.0.0.1/8080 in your browser
Then test and run the API using web dev tools, such as fetch

# Automatically Test API Using Unittest
```
cd api/
python3 unitTests.py
```
Write more when new features are added

# Manually Test API Using Fetch()
Open Chrome Dev Tools, then go to Console.
Use the below template and modify as required
For example:
```
await fetch("http://127.0.0.1/api/Auth", {
  "headers": {
    "accept": "*/*",
    "Access-Control-Allow-Origin": "*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "text/plain;charset=UTF-8"
  },
  "body": "{\"username\":\"lkajsflkjsd\",\"hash\":\"$2a$10$zpb9VY35dH.fY25ff6Tflek907g/ZOel.qGRgANfr/4WY16eECioG\",\"salt\":\"$2a$10$zpb9VY35dH.fY25ff6Tfle\"}",
  "method": "POST",
  "mode": "no-cors",
  "credentials": "omit"
}).then((rz) => rz.text());
```
You could change the last line to:
`}).then((r) => r.json());`
You could change `method` to `GET`,
or body to something else,
or add your query on to the end of the URL on the 1st line

# Notes
* All parameters are passed as variable `D`
* Organized into endpoints from `/api/EndPointHere`
* Queries for `GET` are passed through standard `/api/endpoint?var1=data&var2=moreData` 
* Data for `POST` are passed through the body section of the `fetch()` request

# How to Write a new Endpoint
1. Add a human readable name for the actual endpoint like `/api/CHATROOM`, or something else in `opNames`
2. Add a `tuple` storing `(GET-FUNC,POST-FUNC)` to `opFuncs`, this should be imported from another file
3. Go make a new file and write a `GET-FUNC` and if you don't need a `POST-FUNC`, use `NYI` from `common.py`

# How to Access LMDB
Our custom wrapper is in dblib.py. It does the hard work for us!
1. Opening a DB
```
from dblib import LMDB
exampleDB : LMDB = LMDB('FileName')
# That's it!
```
2. Getting Data from DB
```
# There are 3 ways
# difference is that they return data in a different type
# char buffer, string, JSON
index='Toshiba'
exampleDB.get(index) # returns a char buffer of data in index
exampleDB.sget(index) # returns a string of data in index
# The above is probably most used
exampleDB.jget(index) # returns a JSON object of the data in index
```
3. Putting Data to DB
```
import ujson as js
# We use ujson instead of standard Python bcz UJSON is fast
# There are 2 ways
# difference is that the value being put can be of different type
# string and JSON
# The Key is always a String
jsonObj = { 'Pentium' : '3GB' }
exampleDB.put('schoolLaption','Pentium') # Using a String
exampleDB.put('server',js.dumps(jsonObj))
# Store a list
hoursSlept = 3,6,10 # Abdul, Cian, Veeral
exampleDB.put('hoursToSleep', hoursSlept[0] + ',' + hoursSlept[1] + ',' + hoursSlept[2])
# then to read it, use split(',')
```
4. Other Stuff
```
exampleDB.delt('key') #delete key
print(exampleDB.length) # get length
exampleDB.display() # Debug all data
exampleDB.close() # proper way to stop
```

# Warning
## Heavily Untested, Probably will Crash##
