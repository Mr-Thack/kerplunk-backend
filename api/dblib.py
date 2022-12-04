import cython
import lmdb
import os
import ujson as js


# This is a nice big wrapper for LMDB
class LMDB:
    def __init__(self,path):
        self.path : str = os.getcwd() + '/data/' + path
        # We store all the data in curPath/data/filepath
        # This allows for storing data in directories,
        # but we'd have to make the directory first
        # before the below self.initialize()
        self.initialize()
    def initialize(self):
        print('NEW INSTANCE BEING OPENED OF ' + self.path)
        # Print out intentions
        try:
            print('Opening DB')
            self.env = lmdb.open(self.path, map_size = 104857600*40, subdir=True )
            # The above parameters could change in the future as we expand
            # As of now, we just tell it to open file at self.path
            # with around 100M of data mapped to RAM, using subdirectories
            # I believe it only opens once and runs,
            # (and is shared between instances),
            # so if it crashes, it's not reopening the DB,
            # So I allowed it to open up a whole 100M
            # 104857600 Bytes = 100M
            # For example, if we don't need to save something on disk
            # like a temporary chatroom with no data being saved,
            # we could use writemap=True to only write to RAM
        except Exception as e: # if failed
            print('Failed to open DB: ' + self.path + ' because of:\n' + e)
            quit(0)
    def put(self, key: str, value: str) -> bool: # returns success
        # it writes strings to mem
        try:
            # TODO: I'm thinking we could be more effecient and use plain ASCII
            # instead of UTF8, but we'd have to research on that
            txn = self.env.begin(write=True) # write=True means 'write to disk'
            txn.put(key.encode(), value.encode()) # encode into utf8 (by default)
            txn.commit() # commit to mem
            return True
        except Exception as e:
            print('Failed put: ' + e)
            return False
    def jput(self,key: str, value) -> bool: #returns success
        # value is a JSON object
        try:
            self.put(key,js.dumps(value)) #dump the JSON to string
            return True
        except (Exception) as e:
            print('Failed jput: ' + e)
            return False
    def delt(self, key: str) -> bool: #delete a key
        try:
            txn = self.env.begin(write=True) # write to mem = true
            txn.delete(key.encode()) # key must be in utf8?
            txn.commit()
            return True
        except Exception as e:
            print('Failed delete: '  +e)
            return False
    def get(self, key: str):
        # Gets a char buffer
        try:
            txn = self.env.begin()
            return txn.get(key.encode())
        except Exception as e:
            print('Failed get: ' + e)
            return None
    def sget(self,key: str) -> str:
        #Gets A String
        try:
            rz = self.get(key)
            if not rz:
                return None
            return self.get(key).decode()
        except Exception as e:
            print('Failed sget: ' + e)
            return None
    def jget(self, key: str):
        #Gets a JSON Object
        try:
            rz = self.get(key)
            if not rz:
                return None
            return js.loads(self.get(key))
        except (Exception) as e:
            print("Failed jget: " + e)
            return None
    def length(self): # return amount of entries
        return self.env.stat()['entries']
    def display(self) -> None:
        # To Debug all values
        print(self.env.stat()) # get env
        txn = self.env.begin()
        cur = txn.cursor() # dunno what this does, I guess it gets all indices
        for key, value in cur: # I found this one on the internet
            print('Key: ' + key.decode("utf-8"))
            print('Value: ' + self.get(key.decode("utf-8")) + "\n")
    def close(self) -> None:
        # This should be done, but it doesn't seem to cause harm if it isn't
        self.env.close()
