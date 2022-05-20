#!/usr/bin/python3

from huobi.client.trade import TradeClient
from huobi.constant import *
from huobi.utils import *


trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
symbol = "eth3lusdt"
list_obj = trade_client.get_orders(symbol=symbol, order_state=OrderState.SUBMITTED,
                                    order_type=OrderType.BUY_LIMIT, start_date=None, end_date=None,
                                   start_id=None, size=None, direct=QueryDirection.PREV)

LogInfo.output("===== step 1 ==== {symbol} {count} orders found".format(symbol=symbol, count=len(list_obj)))
if len(list_obj):
    LogInfo.output_list(list_obj)

