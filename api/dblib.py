import lmdb
from os import path, mkdir
from orjson import dumps, loads
# from ormsgpack import packb, unpackb
# I wanted to use ormsgpack, bcz it's based off of orjson and it's super fast
# It uses the msgpack format instead of the JSON format, so it's waay faster
# However, it doesn't seem to build right without the nightly Rust Compiler
# from dataclasses import is_dataclass


PATH = '../data/'  # Default Path
# I'm hoping this is only run once
# If this is being run multiple times, tell me plz -Abdul Muqeet

if not path.exists(PATH):
    print("""You don't seem to have the data folder.\n
          AUTOMATICALLY GENERATING DATA FOLDER!\n
          IF THIS IS ON THE SERVER, WE HAVE ERROR! ABORT NOW!
          """)
    mkdir(PATH)
elif not path.isdir(PATH):
    print(PATH + " IS NOT A DIRECTORY! ABORT!")
    quit(1)


print('OPENING ENVIRONMENTS')
# OK, so I figured out what writemap does,
# basically, it's super fast, but if the server crashes, all the data's gone
# Sooo we're only enabling that for the tmp environments,
# unless we're sure that the server won't crash.
# But the fact of the matter is that it probably will
mainenv = lmdb.open(PATH + 'main', max_dbs=4, writemap=False, subdir=True)
chatenv = lmdb.open(PATH + 'chats', map_size=(10 << 20)*10, max_dbs=100,
                    writemap=True, subdir=True)
# I don't think the users care too much about their old text messages
# I think...
tmpenv = lmdb.open(PATH + 'userdata', max_dbs=1, writemap=True,
                   sync=False, subdir=True)


# Not sure what the safety concerns of writemap=True are, but they exist!
# This is a nice big wrapper for LMDB
class db:
    def __init__(self, name: str, schema, chat=False, tmp=False):
        self.name = name
        self.schema = schema
        self.fields = tuple(schema.__annotations__.keys()) if schema else None
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

    def _fixintindex(self, key: int | str):
        if isinstance(key, int):
            if key < 0:
                key = len(self) - key
            key = str(key)
        return key

    def _serialize(self, obj):
        if not isinstance(obj, dict):
            obj = obj.__dict__
        return dumps(obj)

    def _deserialize(self, vals):
        return loads(vals)

    def _deserialize_schema(self, vals):
        return self.schema(**self._deserialize(vals))

    def __setitem__(self, key: str, value):
        """Simplified Writing To Disk"""
        txn = self.env.begin(db=self.db, write=True)  # write to disk
        if not isinstance(key, tuple):
            key = self._fixintindex(key)
            if isinstance(key, str):
                key = bytes(key, 'utf-8')
            if self.schema:
                value = self._serialize(value)
            elif isinstance(value, str):
                value = bytes(value, 'utf-8')
            elif isinstance(value, int):
                value = bytes(str(value), 'utf-8')
            txn.put(key, value)
        else:
            if key[1] not in self.fields:
                raise KeyError
            obj = self._deserialize(str(txn.get(bytes(key[0], 'utf-8')),
                                        'utf-8'))
            obj[key[1]] = value
            txn.put(bytes(key[0], 'utf-8'), self._serialize(obj))
        return txn.commit()  # commit to mem

    def __delitem__(self, key: str | int):
        """Delete value of a key from DB"""
        print(key)
        key = self._fixintindex(key)
        txn = self.env.begin(db=self.db, write=True)
        txn.delete(bytes(key, 'utf-8'))
        return txn.commit()

    def _coreget(self, key):
        r = self.env.begin(db=self.db).get(bytes(key, 'utf-8'))
        if r:
            return str(r, 'utf-8')
        else:
            return None

    def __getitem__(self, key: str | tuple[str, str]):
        """Gets a String"""
        key = self._fixintindex(key)
        # 1st we'll try to force to a string
        if isinstance(key, str):
            data = self._coreget(key)
            if data and self.schema:
                return self._deserialize_schema(data)
            else:
                return data
        elif isinstance(key, tuple):
            if key[1] not in self.fields:
                raise KeyError
            data = self._coreget(key[0])
            if data:
                return self._deserialize(data)[key[1]]
            else:
                return data
        else:
            raise TypeError('ERROR!!!! __getitem__ dblib!\n' +
                            f'Type {type(key)} not supported!!!!')
            quit(0)

    def __len__(self, e=False):
        """Return amount of entries/dbs"""
        if e:  # e is for environment
            return self.env.stat()['entries']
        else:
            return self.env.begin().stat(self.db)['entries']

    def __iter__(self):
        self.cursor = self.env.begin(db=self.db).cursor()
        return self

    def __next__(self):
        if not self.cursor.next():
            self.cursor.close()
            raise StopIteration
        if not self.schema:
            return (str(self.cursor.key(), 'utf-8'),
                    str(self.cursor.value(), 'utf-8'))
        else:
            key = str(self.cursor.key(), 'utf-8')
            return (key, self[key])

    def __repr__(self):
        ret = ''
        for key, val in self:
            ret += key + ':' + str(val) + "\n"
        return ret

    def display(self):
        """To Debug all values/dbs"""
        print('START DEBUG')
        print(self.env.stat())
        print(self)
        print('END DEBUG')

    def keys(self):
        with self.env.begin(db=self.db) as txn:
            return [str(k, 'utf-8') for k in txn.cursor()
                    .iternext(values=False)]

    """
    def close(self):
        # This is for any cleaning up that we would need to do
        # This should be done, but it doesn't seem to cause harm if it isn't
        self.db.close()
    """


"""
# NOTE: As of now, BaseSchema doesn't work as intentded
# seperator is not existant

# Isn't this nice Test Code?
@dataclass
class TestDBSchema(BaseSchema):
    uname: str
    fname: str

testdb = db('test4', None)  # TestDBSchema, tmp=True)
testdb['u1'] = TestDBSchema('Name1', 'FName1')
testdb['u2'] = TestDBSchema('Name2', 'FName2')
testdb['u3'] = TestDBSchema('Name3', 'FName3')
del testdb['u3']
print(testdb['u1', 'uname'])
testdb['u2', 'uname'] = 'NameNew'
print(testdb['u2', 'uname'])
for i in range(10):
    testdb[i] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i]






for i in range(11):
    print(testdb[i])
"""
