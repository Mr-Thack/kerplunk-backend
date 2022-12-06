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
data = {
    'uname':'test',
    'hash':'abcd',
    'email':'test@test.com',
    'salt':'efgh',
    'sid':'', # Will be set in Test01-test030
    'lname':'Newton,Newtownson'
}
# alt vals is used in Test02-test110
# Whenever supportedFields is updated,
# this should also be modified
altvals = {
    'uname':'tester',
    'lname':'Norm,Normski'
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
            'lname':data['lname']
        }
        r = post(url=url('Users'),json=fd).json()
        self.assertEqual(r['changed'],'lname')
    def test030_get_legalname(self):
        """Check if lname value in db is correct"""
        p = {
            'sid':data['sid'],
            'fields':'lname'
        }
        r = get(url=url('Users?'),params=p).json()
        self.assertEqual(r['lname'],data['lname'])
    def test100_multiget(self,key=data):
        """
        Check if getting all values at once works.
        The key is what will be used as benchmark for the returned values.
        By default, it's set to data. test115_check_multipost will set key to altvals
        """
        p = {
            'sid':data['sid'],
            'fields': str(supportedFields).replace(' ','').replace('(','').replace(')','').replace("'",'')
        }
        r = get(url=url('Users?'),params=p).json()
        for f in supportedFields:
            self.assertEqual(r[f],key[f])
    def test110_multipost(self):
        """Change all values"""
        fd = {'sid':data['sid']}
        for k,v in altvals.items():
            fd[k] = v
        r = post(url=url('Users'),json=fd).json()
        self.assertEqual(set(supportedFields),set(r['changed'].split(' ')))
    def test115_check_multipost(self):
        """Check if all new values are properly set"""
        self.test100_multiget(key=altvals)

if __name__=='__main__':
    # Clear data directory
    rmtree('../data/data/')
    mkdir('../data/data/')
    # Start Server as daemon (dies when script ends) on seperate thread
    server = Thread(target=main)
    server.daemon = True
    server.start()
    sleep(1) # To give server time to start
    unittest.main() # start testing!
