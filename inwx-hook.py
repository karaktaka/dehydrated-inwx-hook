#!/usr/bin/env python3
import time
import argparse
import configparser
from pathlib import Path

from INWX.Domrobot import ApiClient
from tldextract import extract

parser = argparse.ArgumentParser()
parser.add_argument('handler', type=str, nargs=argparse.REMAINDER)

args = parser.parse_args()
config = configparser.ConfigParser()

config_file = Path('/etc/dehydrated/inwx-config')
if config_file.exists():
    config.read(config_file)
else:
    config.read("./config")

try:
    username = config['user']['username']
    password = config['user']['password']
    handler = args.handler
except KeyError:
    print("No config file found. No Account available.")
    exit(1)


def create_record(api, data):
    domain = extract(data[1])
    value = data[3]
    method_data = {
        'domain': domain.registered_domain,
        'name': f'_acme-challenge.{domain.subdomain}' if domain.subdomain else '_acme-challenge',
        'type': 'TXT',
        'ttl': '300',
        'content': value
    }

    return api.call_api(api_method="nameserver.createRecord", method_params=method_data)


def delete_record(api, record_id):
    method_data = {'id': record_id}

    return api.call_api(api_method="nameserver.deleteRecord", method_params=method_data)


def get_record_id(api, data):
    domain = extract(data[1])
    value = data[3]
    method_data = {
        'name': f'_acme-challenge.{domain.subdomain}' if domain.subdomain else '_acme-challenge',
        'content': value
    }

    try:
        return api.call_api(api_method="nameserver.info", method_params=method_data)["resData"]["record"][0]["id"]
    except KeyError:
        print("No such Record found. It may have been deleted manually or didn't exist in the first place.")


def login(api, username, password):
    login_result = api.login(username, password)

    if login_result["code"] == 1000:
        return api
    else:
        raise Exception(f'Api login error. Code: {str(login_result["code"])} Message: {login_result["msg"]}')


def logout(api_client):
    api_client.logout()


if __name__ == "__main__":
    if len(handler) > 0:
        if handler[0] == 'deploy_challenge' or handler[0] == 'clean_challenge':
            client = ApiClient(api_url=ApiClient.API_LIVE_URL, debug_mode=False)
            login(client, username, password)

            if handler[0] == "deploy_challenge":
                result = create_record(client, handler)
            elif handler[0] == "clean_challenge":
                record_id = get_record_id(client, handler)
                result = delete_record(client, record_id)

            if result["code"] == 1000:
                print(result["msg"])
                logout(client)
            else:
                logout(client)
                raise Exception(f'Api error. Code: {str(result["code"])} Message: {result["msg"]}')
