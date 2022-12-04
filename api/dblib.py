import cython
import lmdb
import os
import ujson as js

# I'm hoping this is only run once
print('OPENING ENVIRONMENT')
env = lmdb.open('../data', max_dbs=4,writemap=True,subdir=True)


# This is a nice big wrapper for LMDB
class db:
    def __init__(self,name,map_size=(10<<20)*10,memonly=False):
        self.name = name
        self.map_size=map_size
        self.writemap=True
        self.sync=False if memonly else True
        """
        Also, default size is (1MB)*10 Bytes = 10MB,
        writemap=True is dangerous, but really fast.
        I don't completely understand the risks, but I enabled it
        And, memonly will set sync to false, and we never manually call sync afterwards
        """
        self.initialize()
    def initialize(self):
        print('OPENING DB ' + self.name)
        # Print out intentions
        try:
            # The key is set to name
            self.db = env.open_db(bytes(self.name,'utf-8'))
        except Exception as e: # if failed
            print('FAILED TO OPEN DB ' + self.name + ' BCZ:')
            print(e)
            quit(0)
    def put(self, key: str, value: str) -> bool: # returns success
        # it writes strings to mem
        try:
            # TODO: I'm thinking we could be more effecient and use plain ASCII
            # instead of UTF8, but we'd have to research on that
            txn = env.begin(db=self.db,write=True) # write=True means 'write to disk'
            txn.put(bytes(key,'utf-8'), bytes(value,'utf-8')) # encode into utf8 (by default)
            txn.commit() # commit to mem
            return True
        except Exception as e:
            print('Failed put:')
            print(e)
            return False
    def jput(self,key: str, value) -> bool: #returns success
        # value is a JSON object
        try:
            self.put(key,js.dumps(value)) #dump the JSON to string
            return True
        except (Exception) as e:
            print('Failed jput:')
            print(e)
            return False
    def delt(self, key: str) -> bool: #delete a key
        try:
            txn = env.begin(db=self.db,write=True) # write to mem = true
            txn.delete(bytes(key,'utf-8')) # key must be in utf8?
            txn.commit()
            return True
        except Exception as e:
            print('Failed delete:')
            print(e)
            return False
    def get(self, key: str):
        # Gets a char buffer
        try:
            txn = env.begin(db=self.db)
            return txn.get(bytes(key,'utf-8'))
        except Exception as e:
            print('Failed get:')
            print(e)
    def sget(self,key: str) -> str:
        #Gets A String
        try:
            rz = self.get(key)
            if rz:
                return str(rz,'utf-8')
        except Exception as e:
            print('Failed sget:')
            print(e)
    def jget(self, key: str):
        #Gets a JSON Object
        try:
            rz = self.get(key)
            if rz:
                return js.loads(rz)
        except (Exception) as e:
            print("Failed jget:")
            print(e)
    def length(self,e):
        obj = env if e else self.db
        """Return amount of entries/dbs"""
        return obj.stat()['entries']
    def display(self):
        """To Debug all values/dbs"""
        print(env.stat(self.db)) # get env
        txn = env.begin(db=self.db)
        cur = txn.cursor() # dunno what this does, I guess it gets all indices
        for key, value in cur: # I found this one on the internet
            print('Key: ' + str(key,'utf-8'))
            print('Value: ' + str(self.get(str(key,'utf-8')),'utf-8') + "\n")
    def close(self):
        # This should be done, but it doesn't seem to cause harm if it isn't
        self.db.close()
