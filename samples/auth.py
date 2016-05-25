# -*- coding: utf-8 -*-
# Copyright (c) 2016 Ricoh Co., Ltd. All Rights Reserved.

"""auth sample"""
from __future__ import print_function
import json
from ricohapi.auth.client import AuthClient


def main():
    """ main """
    with open('./config.json', 'r') as settings:
        config = json.load(settings)
        client_id = config['CLIENT_ID']
        client_secret = config['CLIENT_SECRET']
        user_id = config['USER']
        user_pass = config['PASS']

    client = AuthClient(client_id, client_secret)

    client.set_resource_owner_creds(user_id, user_pass)
    client.session(AuthClient.SCOPES['MStorage'])
    print(client.get_access_token())

if __name__ == '__main__':
    main()
