import lmdb
from dataclasses import dataclass

PATH = '../data/'  # Default Path
# I'm hoping this is only run once
# If this is being run multiple times, tell me plz -Abdul Muqeet
print('OPENING ENVIRONMENT')
mainenv = lmdb.open(PATH + 'main', max_dbs=4, writemap=True, subdir=True)
chatenv = lmdb.open(PATH + 'chats', map_size=(10 << 20)*10, max_dbs=100,
                    writemap=True, subdir=True)
tmpenv = lmdb.open(PATH + 'userdata', max_dbs=1, writemap=True,
                   sync=False, subdir=True)


# Not sure what the safety concerns of writemap=True are, but they exist!
# This is a nice big wrapper for LMDB
class db:
    def __init__(self, name: str, schema,
                 env=mainenv, chat=False, tmp=False, seperator=' '):
        self.name = name
        self.schema = schema
        self.fields = tuple(schema.__annotations__.keys())
        self.seperator = seperator
        if tmp:
            self.env = tmpenv
        elif chat:
            self.env = chatenv
        else:
            self.env = mainenv
        print('OPENING DB ' + self.name)
        try:
            # The key is set to name
            self.db = self.env.open_db(bytes(self.name, 'utf-8'))
        except Exception as e:  # if failed
            print('ERR OPEN DB ' + self.name + ' @ ' + self.env.path() + ' BC')
            print(e)
            quit(0)





    def __split2objstr__(self, vals: list[str]):
        s = self.schema(**dict(zip(self.fields, vals)))
        return s

    def __setitem__(self, key: str, value):
        """Simplified Writing To Disk"""
        txn = self.env.begin(db=self.db, write=True)  # write to disk
        if isinstance(key, str):
            # Whether str(str) doesn't error somehow, so this's fine
            txn.put(bytes(key, 'utf-8'), bytes(str(value), 'utf-8'))
        else:
            if key[1] not in self.fields:
                raise KeyError
            toput = str(txn.get(bytes(key[0], 'utf-8')),
                        'utf-8').split(self.seperator)
            toput[self.fields.index(key[1])] = value
            txn.put(bytes(key[0], 'utf-8'), bytes(str(self.__split2objstr__(toput)), 'utf-8'))
        return txn.commit()  # commit to mem

    def __delitem__(self, key: str):
        """Delete value of a key from DB"""
        txn = self.env.begin(db=self.db, write=True)
        txn.delete(bytes(key, 'utf-8'))
        return txn.commit()

    def __formatget__(self, val: str | None):
        if val is None:
            return None
        return self.__split2objstr__(val.split(self.seperator))

    def __coreget__(self, key: str):
        return str(self.env.begin(db=self.db)
                   .get(bytes(key, 'utf-8')), 'utf-8')

    def __getitem__(self, key: str | tuple[str, str]):
        """Gets a String"""
        if isinstance(key, str):
            if self.schema:
                s = self.__coreget__(key)
                return self.__formatget__(s)
            else:
                return self.__coreget_(key)
        else:
            if key[1] not in self.fields:
                raise KeyError
            indx: int = self.fields.index(key[1])
            r = self.__coreget__(key[0])
            if r is None:
                return None
            else:
                r = r.split(self.seperator)
                return r[indx]

    def __len__(self, e=False):
        """Return amount of entries/dbs"""
        obj = self.env if e else self.db
        return obj.stat()['entries']

    def __iter__(self):
        self.cursor = self.env.begin(db=self.db).cursor()
        return self

    def __next__(self):
        if not self.cursor.next():
            self.cursor.close()
            raise StopIteration
        return (str(self.cursor.key(), 'utf-8'),
                str(self.cursor.value(), 'utf-8'))

    def __repr__(self):
        ret = ''
        for k, v in self.env.begin(db=self.db).cursor():
            ret += str(k, 'utf-8') + ':' + str(v, 'utf-8') + "\n"
        return ret

    def display(self):
        """To Debug all values/dbs"""
        print('START DEBUG')
        print(self.env.stat())
        print(self)
        print('END DEBUG')

    """
    def close(self):
        # This is for any cleaning up that we would need to do
        # This should be done, but it doesn't seem to cause harm if it isn't
        self.db.close()
    """


# NOTE: As of now, BaseSchema doesn't work as intentded
# seperator is not existant

class BaseSchema():
    def __str__(self):
        return ' '.join([val or ' ' for val in self.__dict__.values()])

"""
# Isn't this nice Test Code?
@dataclass
class TestDBSchema(BaseSchema):
    uname: str
    fname: str


testdb = db('test4', TestDBSchema, tmp=True)

testdb['u1'] = TestDBSchema('Name1', 'FName1')
testdb['u2'] = TestDBSchema('Name2', 'FName2')
testdb['u3'] = TestDBSchema('Name3', 'FName3')
del testdb['u3']
print(testdb['u1', 'uname'])
testdb['u2', 'uname'] = 'NameNew'
print(testdb['u2', 'uname'])
for k, v in testdb:
   print(f'{k}:{v}')
"""
