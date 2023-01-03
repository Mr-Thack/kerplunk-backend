#!/usr/bin/python3
import unittest
from requests import get, post, put
from threading import Thread
from time import sleep
from devapi import main as server_main
from os import mkdir
from shutil import rmtree  # NOTE: To reduce bloat, we need to get rid of this

# ALERT: Set this to True for debugging
DEBUG = False

# ALERT: When writing new unittests, pay attention to the name's number
# TestUser's data
supported_fields = ('uname', 'lname')


class User():
    def __init__(self, un: str, uhash: str, email: str,
                 salt: str, sid: str, ln: str):
        self.uname: str = un
        self.hash: str = uhash
        self.email: str = email
        self.salt: str = salt
        self.sid: str = sid
        self.lname: str = ln


class Chat():
    def __init__(self, n: str, p: str = '', o: str = '',
                 port: int = 0, ps: list[str] = []):
        self.name: str = n
        self.pwd: str = p
        self.port: int = port
        self.owner: str = o
        self.participants: list[str] = ps


user1: User = User('test', 'abcd', 'test@test.com', 'efgh',
                   '', 'Newton,Newtonson')
# alt vals is used in Test02-test110
# Whenever supported_fields is updated,
# this should also be updated (On New Features)
altvals = {
    'uname': 'tester',
    'lname': 'Norm,Normski'
}

# This is a second user
user2: User = User('test2', 'seconduser',
                   'test2@test.com', 'zxcvbn', '', 'Sleepy,Sleeper')
users = (user1, user2)
chat1: Chat = Chat('Testing')
chat_rooms = (chat1, )


def url(addr):
    return 'http://127.0.0.1:8000/api/' + addr


def sget(addr: str, params: dict = {}):
    r = get(url=url(addr), params=params)
    if DEBUG:
        print('GET to ' + addr + ' returned:\n' + str(r.content))
    return r.json()


def spost(addr: str, form_data: dict):
    r = post(url=url(addr), json=form_data)
    if DEBUG:
        print('POST to ' + addr + ' returned:\n' + str(r.content))
    return r.json()


def sput(addr: str, data: dict):
    r = put(url=url(addr), data=data)
    if DEBUG:
        print('PUT to ' + addr + ' returned:\n' + str(r.content))
    return r.json()


def sign_up_user(user: User):
    fd = {
        'username': user.uname,
        'hash': user.hash,
        'email': user.email,
        'salt': user.salt
    }
    return spost('auth', fd)['error']


def get_user_salt(user: User):
    p = {
        'username': user.uname
    }
    return sget('auth?', p)['salt']


def get_user_sid(user: User):
    p = {
        'username': user.uname,
        'hash': user.hash
    }
    return sget('auth?', p)['sid']


class Test010_auth(unittest.TestCase):
    def test010_make_user(self):
        """Sign up test user"""
        error = sign_up_user(user1)
        self.assertFalse(error)

    def test020_get_salt(self):
        """Get Back Salt"""
        salt = get_user_salt(user1)
        self.assertEqual(salt, user1.salt)

    def test030_get_sid(self):
        """
        Generate an SID, Must be done after we
        get the salt in test020_get_salt above
        """
        sid = get_user_sid(user1)
        self.assertTrue(sid)
        user1.sid = sid

    def test040_login_second_user(self):
        sign_up_user(user2)
        get_user_salt(user2)  # We don't need the salt in this case
        sid = get_user_sid(user2)
        self.assertTrue(sid)
        user2.sid = sid


class Test020_User_Data(unittest.TestCase):
    def test010_get_username(self):
        """Check if test user's username is correctly registered"""
        p = {
            'sid': user1.sid,
            'fields': 'uname'
        }
        r = sget('users?', p)
        self.assertTrue(r['uname'])
        self.assertEqual(r['uname'], user1.uname)

    def test020_set_legalname(self):
        """Set lname value in db"""
        fd = {
            'sid': user1.sid,
            'lname': user1.lname
        }
        r = spost('users', fd)
        self.assertEqual(r['changed'], 'lname')

    def test030_get_legalname(self):
        """Check if lname value in db is correct"""
        p = {
            'sid': user1.sid,
            'fields': 'lname'
        }
        r = sget('users?', p)
        self.assertEqual(r['lname'], user1.lname)

    def test100_multiget(self, key=user1):
        """
        Check if getting all values at once works.
        The key is what will be used as benchmark for the returned values.
        test120_check_multipost will set key to altvals
        """
        p = {
            'sid': user1.sid,
            'fields': str(supported_fields)
                        .replace(' ', '').replace('(', '')
                        .replace(')', '').replace("'", '')
        }
        r = sget('users?', p)
        if isinstance(key, dict):
            key = key.__dict__  # FORM INTO DICT
        for f in supported_fields:
            # Class.__dict__ is a quick way to get it done, apparently
            self.assertEqual(r[f], key[f])

    def test110_multipost(self):
        """Change all values"""
        fd = {'sid': user1.sid}
        for k, v in altvals.items():
            fd[k] = v
        r = spost('users', fd)
        self.assertEqual(set(supported_fields), set(r['changed'].split(' ')))

    def test120_check_multipost(self):
        """Check if all new values are properly set, after 110_multipost"""
        self.test100_multiget(key=altvals)
        user1.uname = altvals['uname']
        user1.lname = altvals['lname']


class Test030_Chat_Rooms(unittest.TestCase):
    def test010_open_chat_room(self):
        """Check if API can create chat rooms"""
        fd = {
            'sid': user1.sid,
            'name': chat_rooms[0].name,
            'pwd': chat_rooms[0].pwd,
            'public': True,
            'temp': True
        }
        r = spost('chatrooms', fd)
        self.assertFalse(r['error'])

    def test020_list_chat_rooms(self):
        """Check if API returns correct list of chat rooms"""
        # No SID required because this doesn't really need authentication
        # And no parameters required
        r = sget('chatrooms')
        self.assertEqual(r['chats'], chat_rooms[0].name)

    def test030_first_user_join_chat(self):
        """Check what data is being given back from the
        first time a user joins the chat"""
        chat: Chat = chat_rooms[0]
        d = {
            'sid': user2.sid,
            'name': chat_rooms[0].name
        }
        r = sput('chatrooms', d)
        self.assertFalse(r['error'])
        self.assertEqual(r['port'], 6000)
        # Should be the very first port, & we start from 6000
        self.assertMultiLineEqual(r['owner'], user1.uname)
        self.assertListEqual(r['joiners'], [user2.uname])
        chat.owner = r['owner']
        chat.port = r['port']
        chat.pwd = ''


if __name__ == '__main__':
    # Clear data directory
    rmtree('../data/data/')
    # NOTE: We need to eventually implement our own rmtree,
    # because it's a waste of bandwidth installing a whole library
    # to do something relatively simple, recursively removing a directory
    mkdir('../data/data/')
    # Start Server as daemon (dies when script ends) on seperate thread
    server = Thread(target=server_main)
    server.daemon = True
    server.start()
    sleep(1)  # To give server time to start
    unittest.main()
