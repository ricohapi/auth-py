# -*- coding: utf-8 -*-
# Copyright (c) 2016 Ricoh Co., Ltd. All Rights Reserved.

from unittest import TestCase
from nose.tools import eq_, raises
import mock
from mock import Mock
from requests.exceptions import RequestException
from ricohapi.auth.client import AuthClient

class TestInit(TestCase):
    @raises(TypeError)
    def test_param_err1(self):
        AuthClient()

    @raises(TypeError)
    def test_param_err2(self):
        AuthClient('a')

    def test_ok(self):
        t = AuthClient('a', 'b')
        eq_(t._AuthClient__client_params['client_id'], 'a')
        eq_(t._AuthClient__client_params['client_secret'], 'b')

class TestROC(TestCase):
    def setUp(self):
        self.target = AuthClient('cid', 'cpass')

    @raises(TypeError)
    def test_param_err1(self):
        self.target.set_resource_owner_creds()

    @raises(TypeError)
    def test_param_err2(self):
        self.target.set_resource_owner_creds('c')

    def test_ok(self):
        self.target.set_resource_owner_creds('c','d')
        eq_(self.target._AuthClient__user_params['username'], 'c')
        eq_(self.target._AuthClient__user_params['password'], 'd')

class TestSession(TestCase):
    def setUp(self):
        self.target = AuthClient('cid', 'cpass')
        self.target.set_resource_owner_creds('c','d')

    @mock.patch('requests.post')
    def test_ok(self, req):
        req.return_value.text = '{"access_token": "atoken","https://ucs.ricoh.com/scope/api/udc2":{"access_token":"atoken2", "refresh_token":"rtoken", "expires_in":179}}'
        ret = self.target.session(AuthClient.SCOPES['MStorage'])
        eq_(ret, {'access_token': 'atoken2', 'expires_in': 179, 'refresh_token': 'rtoken'})

    @raises(ValueError)
    @mock.patch('requests.post')
    def test_json_exception(self, req):
        req.return_value.text = 'not json'
        ret = self.target.session(AuthClient.SCOPES['MStorage'])

    @raises(ValueError)
    @mock.patch('requests.post')
    def test_key_error(self, req):
        req.return_value.text = '{"abc": 10}'
        ret = self.target.session(AuthClient.SCOPES['MStorage'])

    @raises(RequestException)
    @mock.patch('requests.post')
    def test_requests_exception(self, req):
        req.side_effect = RequestException
        ret = self.target.session(AuthClient.SCOPES['MStorage'])


class TestGetAccessToken(TestCase):
    def setUp(self):
        self.target = AuthClient('cid', 'cpass')
        self.target.set_resource_owner_creds('c','d')

    @mock.patch('requests.post')
    def test_refresh_ok(self, req):
        req.return_value.text = '{"access_token": "atoken","https://ucs.ricoh.com/scope/api/udc2":{"access_token":"atoken2", "refresh_token":"rtoken", "expires_in":179}}'
        self.target.session(AuthClient.SCOPES['MStorage'])
        req.return_value.text = None
        ret = self.target.get_access_token()
        eq_(ret, 'atoken2')

    @mock.patch('requests.post')
    def test_refresh_expire_ok(self, req):
        req.return_value.text = '{"access_token": "atoken","https://uaccess_token":"atoken2", "refresh_token":"rtoken", "expires_in":179}'
        ret = self.target.get_access_token()
        eq_(ret, 'atoken')

    @raises(ValueError)
    @mock.patch('requests.post')
    def test_json_exception(self, req):
        req.return_value.text = 'not json'
        ret = self.target.get_access_token()

    @raises(RequestException)
    @mock.patch('requests.post')
    def test_exception(self, req):
        req.side_effect = RequestException
        ret = self.target.get_access_token()
