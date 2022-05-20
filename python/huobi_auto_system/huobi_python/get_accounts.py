#!/usr/bin/python3

from huobi.client.account import AccountClient
from huobi.constant import *

# get accounts
from huobi.utils import *
from configparser import ConfigParser

ini_file = "hunter.ini"
cfg = ConfigParser()
cfg.read(ini_file)

general_cfg = dict(cfg.items('general'))
g_api_key = general_cfg['g_api_key']
g_secret_key = general_cfg['g_secret_key']

account_client = AccountClient(api_key=g_api_key,
                              secret_key=g_secret_key)

list_obj = account_client.get_accounts()
LogInfo.output_list(list_obj)

