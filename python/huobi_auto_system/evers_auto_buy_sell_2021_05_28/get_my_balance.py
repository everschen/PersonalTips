#!/usr/bin/python3

from huobi.client.account import AccountClient, AccountBalance, get_default_server_url, AccountType
from huobi.privateconfig import *
from huobi.client.wallet import WalletClient
from huobi.service.wallet.get_deposit_withdraw import GetDepositWithdrawService
from huobi.constant.definition import *
from huobi.constant import *
from huobi.utils import *

g_api_key = "XXXXXXX"
g_secret_key = "XXXXXXX"


account_client = AccountClient(api_key=g_api_key, secret_key=g_secret_key)
account_balance_list = account_client.get_account_balance()
if account_balance_list and len(account_balance_list):
    for account_balance_obj in account_balance_list:
        if account_balance_obj and len(account_balance_obj.list):
            PrintBasic.print_basic(account_balance_obj.id, "ID")
            PrintBasic.print_basic(account_balance_obj.type, "Account Type")
            PrintBasic.print_basic(account_balance_obj.state, "Account State")
            PrintBasic.print_basic(account_balance_obj.subtype, "Subtype")
            for balance_obj in account_balance_obj.list:
                if float(balance_obj.balance) > 0.1:  # only show account with balance
                    balance_obj.print_object("\t")
                    print()
        print()


