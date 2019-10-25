#!/usr/bin/env python3
import time
import argparse
import configparser
from pathlib import Path

from INWX.Domrobot import ApiClient
from tldextract import extract

parser = argparse.ArgumentParser()
parser.add_argument('handler', type=str, nargs='+')

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


# noinspection PyUnboundLocalVariable
if handler[0] == "deploy_challenge":
    api_client = ApiClient(api_url=ApiClient.API_LIVE_URL, debug_mode=False)
    # noinspection PyUnboundLocalVariable
    login_result = api_client.login(username, password)

    if login_result["code"] == 1000:
        result = create_record(api_client, handler)
        if result["code"] == 1000:
            print("Wait 60 seconds for changes to propagate.")
            time.sleep(60)
            print(result["msg"])

        api_client.logout()
    else:
        raise Exception(f'Api login error. Code: {str(login_result["code"])} Message: {login_result["msg"]}')
