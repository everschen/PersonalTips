#!/usr/bin/python3

from huobi.client.trade import TradeClient
from huobi.constant import *
from send_email_fun import send_email
from huobi.utils import *
import sys
import re
from autonomy import __Autonomy__

from configparser import ConfigParser

ini_file = "hunter.ini"
cfg = ConfigParser()
cfg.read(ini_file)

general_cfg = dict(cfg.items('general'))
g_api_key = general_cfg['g_api_key']
g_secret_key = general_cfg['g_secret_key']

def get_first_value(list_value):
    if len(list_value):
        ret = list_value[0].strip()
    else:
        ret=""
    return ret

def get_value(key, str):
    data=str.split('\n')
    order_id_list = []
    for cur_str in data:
        n = re.findall(key, cur_str)
        if n:
           tmp = cur_str.split(':') 
           if tmp[1].strip():
               order_id_list.append(tmp[1].strip())
    return order_id_list

def get_orders(symbol):
    try:
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)

        list_obj = trade_client.get_orders(symbol=symbol, order_state=OrderState.SUBMITTED,
                                        order_type=None, start_date=None, end_date=None,
                                    start_id=None, size=None, direct=QueryDirection.PREV)
        LogInfo.output("=======================================================================")
        LogInfo.output(" {symbol} {count} orders found".format(symbol=symbol, count=len(list_obj)))
        if len(list_obj):
            LogInfo.output_list(list_obj)

    except Exception as e:
        print("get_orders ExecuteError", e) 
 
def callback(upd_event: 'OrderUpdateEvent'):
    print("---- order update : ----")
    #upd_event.print_object()

    try:
        b = __Autonomy__()
        current = sys.stdout
        sys.stdout = b
        upd_event.print_object()
        sys.stdout = current

        order_type = get_value("Order Type", b._buff)
        price = get_value("Trade Price", b._buff)
        order_state = get_value("Order State", b._buff)
        order_symbol = get_value("Symbol", b._buff)
        order_id = get_value("Order Id", b._buff)
        amount = get_value("Trade Volume", b._buff)

        order_type = get_first_value(order_type)
        order_state = get_first_value(order_state)
        order_symbol = get_first_value(order_symbol)
        price = get_first_value(price)
        price = price if price=="" else float(price)
        order_id = int(get_first_value(order_id))
        amount = get_first_value(amount)
        amount = amount if amount =="" else float(amount)

        print(b._buff)

        if order_type == "sell-limit":
            order_type = "sell"
        elif order_type == "buy-limit":
            order_type = "buy"

        if order_state == "filled":
            order_state = "done"
        elif order_state == "partial-filled":
            order_state = "part done"

        if price or amount:
            order_info = "%s, %s, price=%s, Volume=%s"%(order_type, order_state, price, amount)
        else:
            order_info = "%s, %s"%(order_type, order_state)

        print(order_info)


        current = sys.stdout
        a = __Autonomy__()
        sys.stdout = a
        print(b._buff)
        print("\n===== check SUBMITTED order =====\n")
        get_orders(order_symbol)

        sys.stdout = current
        
        send_email("HB: " + order_info, a._buff)
    except Exception as e:
        print("callback ExecuteError", e)


trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key, init_log=True)
trade_client.sub_order_update("eth3lusdt,eth3susdt,ethusdt,btc3lusdt", callback)
