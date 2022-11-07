import cython
import lmdb
import os
import ujson as js

class LMDB:
    def __init__(self,path):
        self.path : str = os.getcwd() + '/data/' + path
        self.initialize()
    def initialize(self):
        print('NEW INSTANCE BEING OPENED OF' + self.path)
        self.env = None
        try:
            print('Opening DB')
            self.env = lmdb.open(self.path, map_size = 104857600*40, subdir=True ) #104857600 100M
        except Exception as e:
            print(e)
            self.env = None
        if self.env is None:
            print("Failed to Open DB")
            quit(0)
    def put(self, key: str, value: str) -> bool:
        # I dunno what'll happen if the key is more than 16 bytes
        # or if the value is more than 64, probably nothing, but who knows!
        try:
            txn = self.env.begin(write=True)
            txn.put(key.encode(), value.encode())
            txn.commit()
        except Exception as e:
            print(e)
            return False
        return True
    def jput(self,key: str, value) -> bool: #value is an object
        try:
            self.put(key,js.dumps(value))
        except (Exception) as e:
            print(e)
            return False
        return True
    def delt(self, key: str) -> bool:
        try:
            txn = self.env.begin(write=True)
            txn.delete(key.encode())
            txn.commit()
            return True
        except Exception as e:
            print(e)
            return False
    def get(self, key: str):# -> cython.char[64]:
        txn = self.env.begin()
        return txn.get(key.encode())
    def sget(self,key: str) -> str:
        #Gets A String
        try:
            return self.get(key).decode()
        except:
            return None
    def jget(self, key: str):
        #Gets a JSON Object
        try:
            return js.loads(self.get(key))
        except (Exception) as e:
            print("error in jget")
            print(e)
            return None
    def length(self):
        return self.env.stat()['entries']
    def display(self) -> None:
        # To Debug all values
        txn = self.env.begin()
        cur = txn.cursor()
        for key, value in cur:
            print(key.decode("utf-8"))
            print(self.get(key.decode("utf-8")) + "\n")
    def close(self) -> None:
        self.env.close()
