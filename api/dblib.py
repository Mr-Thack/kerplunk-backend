import cython
import lmdb
import os
import ujson as js

PATH='../data/data/' # Default Path
# I'm hoping this is only run once
print('OPENING ENVIRONMENT')
mainenv = lmdb.open(PATH+'main', max_dbs=4,writemap=True,subdir=True)
chatenv = lmdb.open(PATH+'chats',map_size=(10<20)*10,max_dbs=10,writemap=True,subdir=True)

# Not sure what the safety concerns of writemap=True are, but they do indeed exist!

# This is a nice big wrapper for LMDB
class db:
    def __init__(self,name,tmp=False,chat=False):
        self.name = name
        if tmp:
            self.env = lmdb.open('/tmp/Data',max_dbs=1,map_size=10<<20,writemap=True,sync=False,subdir=True)
        elif chat:
            self.env = chatenv
        else:
            self.env = mainenv
        self.initialize()
    def initialize(self):
        """Open a Database (Equivalent of an SQL Table)"""
        print('OPENING DB ' + self.name)
        try:
            # The key is set to name
            self.db = self.env.open_db(bytes(self.name,'utf-8'))
        except Exception as e: # if failed
            print('FAILED TO OPEN DB ' + self.name + ' at ' + self.env.path() + ' BCZ:')
            print(e)
            quit(0)
    def put(self, key: str, value: str):
        """Simplified Writing To Disk"""
        try:
            txn = self.env.begin(db=self.db,write=True) # write=True means 'write to disk'
            txn.put(bytes(key,'utf-8'), bytes(value,'utf-8')) # encode into utf8 (by default)
            txn.commit() # commit to mem
            return True
        except Exception as e:
            print('Failed put:')
            print(e)
            return False
    def jput(self,key: str, value) -> bool: #returns success
        """Put Value as a JSON object"""
        try:
            self.put(key,js.dumps(value)) #dump the JSON to string
            return True
        except (Exception) as e:
            print('Failed jput:')
            print(e)
            return False
    def delt(self, key: str) -> bool: #delete a key
        "Safe Delete"
        try:
            txn = self.env.begin(db=self.db,write=True) # write to mem = true
            txn.delete(bytes(key,'utf-8')) # key must be in utf8?
            txn.commit()
            return True
        except Exception as e:
            print('Failed delete:')
            print(e)
            return False
    def get(self, key: str):
        """Gets a Char Buffer"""
        txn = self.env.begin(db=self.db)
        return txn.get(bytes(key,'utf-8'))
    def sget(self,key: str) -> str:
        """Gets a String"""
        rz = self.get(key)
        if rz:
            return str(rz,'utf-8')
    def jget(self, key: str):
        """Gets a JSON Object"""
        rz = self.get(key)
        if rz:
            return js.loads(rz)
    def length(self,e=False):
        """Return amount of entries/dbs"""
        obj = self.env if e else self.db
        return obj.stat()['entries']
    def display(self):
        """To Debug all values/dbs"""
        print(self.env.stat())
        txn = self.env.begin(db=self.db)
        cur = txn.cursor() # dunno what this does, I guess it gets all indices
        for key, value in cur: # I found this one on the internet
            print('Key: ' + str(key,'utf-8'))
            print('Value: ' + str(self.get(str(key,'utf-8')),'utf-8') + "\n")
    def close(self):
        # This should be done, but it doesn't seem to cause harm if it isn't
        self.db.close()
