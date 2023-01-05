#!/usr/bin/python3
import unittest
from dataclasses import dataclass, field
# ALERT: Set to true for performance test
PERF = False
# All it does is not load our Kerplunk backend,
# and thus assumes that our backend is already running

# ALERT: When writing new unittests, pay attention to the name's number
# TestUser's data
supported_fields = ('uname', 'lname')

if PERF:
    from httpx import get, post, put, delete
else:
    from fastapi.testclient import TestClient
    from main import app
    from os import mkdir
    from shutil import rmtree
    # NOTE: To reduce bloat, we need to get rid of this


class performance_test_client():
    def __init__(self, url: str):
        self.url = url

    def get(self, url: str, params={}, headers={}):
        return get(self.url + url, params=params, headers=headers)

    def post(self, url: str, data={}, json={}, headers={}):
        return post(self.url + url, data=data, json=json, headers=headers)

    def patch(self, url: str, json: dict, params: dict, headers: dict):
        return put(self.url + url, json=json, params=params, headers=headers)

    def delete(self, url: str, params: dict):
        return delete(self.url + url, params=params)


def make_client():
    if not PERF:
        return TestClient(app)
    else:
        return performance_test_client('http://127.0.0.1:8000')


client = make_client()


@dataclass
class User:
    uname: str
    pwd: str
    email: str
    sid: str
    lname: str


@dataclass
class Chat:
    name: str
    pwd: str = ''
    cid: str = ''
    owner: str = ''
    participants: list = field(default_factory=lambda: [])


user1: User = User('test', 'abcd', 'test@test.com', '', 'Newton,Newtonson')
# alt vals is used in Test02-test110
# Whenever supported_fields is updated,
# this should also be updated (On New Features)
altvals = {
    'uname': 'tester',
    'lname': 'Norm,Normski'
}

# This is a second user
user2: User = User('test2', 'seconduser', 'test2@test.com', '', 'Slepy,Sleper')
users = (user1, user2)
chat1: Chat = Chat('Testing')
chat_rooms = (chat1, )


def genhed(user: User):
    return {
        'Authorization': 'Bearer ' + user.sid
    }


def sign_up_user(user: User):
    return client.post('/signup', json={
        'uname': user.uname,
        'pwd': user.pwd,
        'email': user.email
    })


def get_user_sid(user: User):
    con = {
        'grant_type': '',
        'username': user.uname,
        'password': user.pwd,
        'scope': '',
        'client_id': '',
        'client_secret': ''
    }
    return client.post('/login', data=con).json()['access_token']


class Test010_auth(unittest.TestCase):
    def test010_make_user(self):
        """Sign up test user"""
        self.assertEqual(sign_up_user(user1).status_code, 200)

    def test020_get_sid(self):
        """
        Generate an SID, Must be done after we
        get the salt in test020_get_salt above
        """
        sid = get_user_sid(user1)
        self.assertIsNotNone(sid)
        user1.sid = sid

    def test030_login_second_user(self):
        sign_up_user(user2)
        sid = get_user_sid(user2)
        self.assertIsNotNone(sid)
        user2.sid = sid


class Test020_User_Data(unittest.TestCase):
    def test010_get_username(self):
        """Check if test user's username is correctly registered"""
        r = client.get('/userme', params={
            'fields': ['uname']
            }, headers=genhed(user1)).json()
        self.assertIn('uname', r)
        self.assertEqual(r['uname'], user1.uname)

    def test020_set_legalname(self):
        """Set lname value in db"""
        r = client.post('/userme', json={'lname': user1.lname},
                        headers=genhed(user1)).json()
        self.assertIn('changed', r)
        self.assertEqual(r['changed'], 'lname')

    def test030_get_legalname(self):
        """Check if lname value in db is correct"""
        r = client.get('/userme', params={
            'fields': 'lname'
            }, headers=genhed(user1)).json()
        self.assertEqual(r['lname'], user1.lname)

    def test100_multiget(self, key=user1, auth_user=user1):
        """
        Check if getting all values at once works.
        The key is what will be used as benchmark for the returned values.
        test120_check_multipost will set key to altvals
        """
        # We need key to be a dictionary, eventually
        if isinstance(key, User):
            key = key.__dict__
        r = client.get('/userme', params={
            'fields': supported_fields
            }, headers=genhed(auth_user)).json()
        for f in supported_fields:
            # Class.__dict__ is a quick way to get it done, apparently
            self.assertEqual(r[f], key[f])

    def test110_multipost(self):
        """Change all values"""
        r = client.post('/userme', json=altvals, headers=genhed(user1)).json()
        self.assertIn('changed', r)
        self.assertSetEqual(set(supported_fields), set(r['changed'].split(' ')))

    def test120_check_multipost(self):
        """Check if all new values are properly set, after 110_multipost"""
        self.test100_multiget(key=altvals)
        user1.uname = altvals['uname']
        user1.lname = altvals['lname']


class Test030_Chat_Rooms(unittest.TestCase):
    def test010_open_chat_room(self):
        """Check if API can create chat rooms"""
        chat: Chat = chat_rooms[0]
        js = {
            'name': chat.name,
            'pwd': chat.pwd,
            'public': True,
            'temp': True
        }
        r = client.post('/chats', json=js, headers=genhed(user1)).json()
        self.assertIn('cid', r)
        chat.cid = r['cid']

    def test020_list_chat_rooms(self):
        """Check if API returns correct list of chat rooms"""
        # No SID required because this doesn't really need authentication
        # And no parameters required
        r = client.get('/chats').json()
        self.assertEqual(r['chatrooms'], chat_rooms[0].name)

    def test030_first_user_join_chat(self):
        """Check what data is being given back from the
        first time a user joins the chat"""
        chat: Chat = chat_rooms[0]
        r = client.patch('/chats', params={
            'name': chat_rooms[0].name
            }, headers=genhed(user2)).json()
        self.assertEqual(r['owner'], user1.uname)
        self.assertEqual(r['cid'], chat.cid)
        self.assertListEqual(r['joiners'], [user2.uname])
        chat.owner = r['owner']
        chat.pwd = ''


if __name__ == '__main__':
    if not PERF:
        # Clear data directory
        rmtree('../data/')
        # NOTE: We need to eventually implement our own rmtree,
        # because it's a waste of bandwidth installing a whole library
        # to do something relatively simple, recursively removing a directory
        mkdir('../data/')
    # Start Server as daemon (dies when script ends) on seperate thread
    # server = Thread(target=server_main)
    # server.daemon = True
    # server.start()
    # sleep(1)  # To give server time to start
    unittest.main()
