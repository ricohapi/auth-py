# -*- coding: utf-8 -*-
# Copyright (c) 2016 Ricoh Co., Ltd. All Rights Reserved.

"""
RICOH API AUTH
"""
import time
from datetime import datetime
import json
import requests

class AuthClient(object):
    """auth client"""
    SCOPES = {
        'MStorage': 'https://ucs.ricoh.com/scope/api/udc2',
        'VStream': 'https://ucs.ricoh.com/scope/api/udc2',
        'CameraCtl': 'https://ucs.ricoh.com/scope/api/udc2',
    }

    @staticmethod
    def __raise_value_error():
        raise ValueError('Could not get an access token to allow your access. '
                         'Make sure that your user ID and password are correct.')

    def __init__(self, client_id, client_secret):
        self.__endpoint = 'https://auth.beta2.ucs.ricoh.com'
        self.__scopes = (
            'https://ucs.ricoh.com/scope/api/auth',
            'https://ucs.ricoh.com/scope/api/discovery'
        )
        self.__client_params = {
            'client_id': client_id,
            'client_secret': client_secret
        }
        self.__user_params = {}
        self.__access_token = ''
        self.__refresh_token = ''
        self.__expire = 0

    def set_resource_owner_creds(self, user, password):
        """Set OAuth Resource Owner Credentials."""
        self.__user_params = {
            'username': user,
            'password': password,
            'grant_type': 'password'
        }

    def __auth(self, scope):
        params = {
            'scope': ' '.join(self.__scopes + (scope,)),
        }
        params.update(self.__client_params)
        params.update(self.__user_params)
        try:
            req = requests.post(self.__endpoint + "/auth/token", data=params)
            req.raise_for_status()
        except requests.exceptions.RequestException:
            raise
        try:
            ret = json.loads(req.text)
        except ValueError:
            AuthClient.__raise_value_error()
        return ret

    def __discovery(self, scope, token):
        params = {
            'scope': scope,
        }
        headers = {
            'Authorization': 'Bearer ' + token
        }
        try:
            req = requests.post(self.__endpoint + "/auth/discovery", headers=headers, data=params)
            req.raise_for_status()
        except requests.exceptions.RequestException:
            raise
        try:
            ret = json.loads(req.text)
        except ValueError:
            AuthClient.__raise_value_error()
        return ret

    def __refresh(self):
        params = {
            'refresh_token': self.__refresh_token,
            'grant_type': 'refresh_token',
        }
        params.update(self.__client_params)
        try:
            req = requests.post(self.__endpoint + "/auth/token", data=params)
            req.raise_for_status()
        except requests.exceptions.RequestException:
            raise
        try:
            ret = json.loads(req.text)
        except ValueError:
            AuthClient.__raise_value_error()
        return ret

    def __store_token_info(self, retval):
        try:
            self.__access_token = retval['access_token']
            self.__refresh_token = retval['refresh_token']
        except KeyError:
            AuthClient.__raise_value_error()
        now = datetime.now()
        margin_sec = 10
        self.__expire = retval['expires_in'] + int(time.mktime(now.timetuple())) - margin_sec

    def session(self, scope):
        """Start session."""
        ret = self.__auth(scope)
        try:
            ret = self.__discovery(scope, ret['access_token'])
            ret = ret[scope]
            self.__store_token_info(ret)
        except KeyError:
            AuthClient.__raise_value_error()
        return ret

    def get_access_token(self):
        """Get AccessToken."""
        now = datetime.now()

        if int(time.mktime(now.timetuple())) < self.__expire:
            return self.__access_token

        ret = self.__refresh()
        self.__store_token_info(ret)
        return self.__access_token
