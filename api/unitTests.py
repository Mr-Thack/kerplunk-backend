#!/usr/bin/python3
import unittest
from requests import get,post
from threading import Thread
from time import sleep
from devapi import main
from os import mkdir
from shutil import rmtree

# ALERT: When writing new unittests, pay attention to the name's number
# TestUser's data
supportedFields = ('uname','lname')
data : dict = {
    'uname':'test',
    'hash':'abcd',
    'email':'test@test.com',
    'salt':'efgh',
    'sid':'', # Will be set in Test01-test030
    'lname':'Newton,Newtownson'
}

def url(addr):
    return 'http://127.0.0.1:8080/api/' + addr


class Test010_Auth(unittest.TestCase):
    def test010_make_user(self):
        """Sign up test user"""
        fd = {
            'username':data['uname'],
            'hash':data['hash'],
            'email':data['email'],
            'salt':data['salt']
        }
        r = post(url=url('Auth'),json=fd).json()
        self.assertEqual(r['error'],'')
    def test020_get_salt(self):
        """Get Back Salt"""
        p = {
            'username':data['uname'],
        }
        r = get(url=url('Auth?'),params=p).json()
        self.assertEqual(r['salt'],data['salt'])
    def test030_get_sid(self):
        """
        Generate an SID, Must be done after we
        get the salt in test020_get_salt above
        """
        p = {
            'username':data['uname'],
            'hash':data['hash']
        }
        r = get(url=url('Auth?'),params=p).json()
        self.assertTrue(r.get('sid'))
        data['sid'] = r['sid']

class Test020_User_Data(unittest.TestCase):
    def test010_get_username(self):
        """Check if test user's username is correctly registered"""
        p = {
            'sid':data['sid'],
            'fields':'uname'
        }
        r = get(url=url('Users?'),params=p).json()
        self.assertEqual(r['uname'],data['uname'])
    def test020_set_legalname(self):
        """Set lname value in db"""
        fd = {
            'sid':data['sid'],
            'field':'lname',
            'val':data['lname']
        }
        r = post(url=url('Users'),json=fd).json()
        self.assertEqual(r['error'],'')
    def test030_get_legalname(self):
        """Check if lname value in db is correct"""
        p = {
            'sid':data['sid'],
            'fields':'lname'
        }
        r = get(url=url('Users?'),params=p).json()
        self.assertEqual(r['lname'],data['lname'])
    def test100_multiget(self):
        """Check if getting all values at once works"""
        p = {
            'sid':data['sid'],
            'fields': str(supportedFields).replace(' ','').replace('(','').replace(')','').replace("'",'')
        }
        r = get(url=url('Users?'),params=p).json()
        for k in r: # k for key
            self.assertEqual(r[k],data[k])

if __name__=='__main__':
    rmtree('../data/data/')
    mkdir('../data/data/')
    server = Thread(target=main)
    server.daemon = True
    server.start()
    sleep(1) # To give server time to start
    unittest.main()
