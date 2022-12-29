import cython
import lmdb
import os
import ujson as js

PATH='../data/data/' # Default Path
# I'm hoping this is only run once
# If there's any proof this is being run multiple times, tell me plz -Abdul Muqeet
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
    def eput(self,key:str,value:str) -> bool:
        """Writing Directly to the environment, not to a sub-db"""
        txn = self.env.begin(write=True)
        txn.put(bytes(key,'utf-8'),bytes(value,'utf-8'))
        return txn.commit()
    def put(self, key: str, value: str) -> bool:
        """Simplified Writing To Disk"""
        txn = self.env.begin(db=self.db,write=True) # write=True means 'write to disk'
        txn.put(bytes(key,'utf-8'), bytes(value,'utf-8')) # encode into utf8 (by default)
        return txn.commit() # commit to mem
    def jput(self,key: str, value) -> bool: #returns success
        """Put Value as a JSON object"""
        return self.put(key,js.dumps(value)) #dump the JSON to string
    def delt(self, key: str,isDB=True) -> bool: #delete a key
        """Delete value of a key from DB"""
        txn = self.env.begin(db=self.db,write=True) if isDB else self.env.begin(write=True)
        txn.delete(bytes(key,'utf-8')) # key must be in utf8?
        return txn.commit()
    def eget(self,key:str):
        """Get a char buf from env not db"""
        return self.env.begin().get(bytes(key,'utf-8'))
    def get(self, key: str):
        """Gets a Char Buffer"""
        return self.env.begin(db=self.db).get(bytes(key,'utf-8'))
    def sget(self,key: str) -> str:
        """Gets a String"""
        rz = self.get(key)
        if rz:
            return str(rz,'utf-8')
    def jget(self, key: str):
        """Gets a JSON Object"""
        rz = js.loads(self.get(key))
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
        for k,v in cur: # I found this one on the internet
            print('Key: ' + str(k,'utf-8'))
            print('Value: ' + str(self.get(str(k,'utf-8')),'utf-8') + "\n")
    def close(self):
        # This should be done, but it doesn't seem to cause harm if it isn't
        self.db.close()
