#!/usr/bin/python3

from huobi.client.trade import TradeClient
from huobi.constant import *
from huobi.utils import *
from autonomy import __Autonomy__
import re
import sys, time
from huobi.client.market import MarketClient
from huobi.client.account import AccountClient
import logging
from send_email_fun import send_email

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

symbol = "eth3lusdt"

price_points = []
state_points = {}

def has_buy_order(symbol, buy_price, sell_price, check_partial):
    try:
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
        list_obj = trade_client.get_orders(symbol=symbol, order_state=OrderState.SUBMITTED,
                                        order_type=None, start_date=None, end_date=None,
                                    start_id=None, size=None, direct=QueryDirection.PREV)
        count=len(list_obj)
        order_type = []
        for obj in list_obj:
            a = __Autonomy__()
            current = sys.stdout
            sys.stdout = a
            obj.print_object()
            sys.stdout = current
            order_type = get_value("Order Type", a._buff)
            price = get_value("Price", a._buff)
            current_price =float(price[0]) 
            if (order_type[0] == "buy-limit"):
                if current_price == buy_price:
                    return True,True
            else:
                if current_price == sell_price:
                    return True,False
    except:
        print("ExecuteError")

    if check_partial:
        try:
            list_obj = trade_client.get_orders(symbol=symbol, order_state=OrderState.PARTIAL_FILLED,
                                            order_type=None, start_date=None, end_date=None,
                                        start_id=None, size=None, direct=QueryDirection.PREV)
            count=len(list_obj)
            order_type = []
            for obj in list_obj:
                a = __Autonomy__()
                current = sys.stdout
                sys.stdout = a
                obj.print_object()
                sys.stdout = current
                order_type = get_value("Order Type", a._buff)
                price = get_value("Price", a._buff)
                current_price =float(price[0]) 
                if (order_type[0] == "buy-limit"):
                    if current_price == buy_price:
                        return True,True
                else:
                    if current_price == sell_price:
                        return True,False
        except:
            print("ExecuteError")
    return False,False

def has_orders(symbol):
    try:
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
        list_obj_submitted = trade_client.get_orders(symbol=symbol, order_state=OrderState.SUBMITTED,
                                        order_type=None, start_date=None, end_date=None,
                                    start_id=None, size=None, direct=QueryDirection.PREV)
        list_obj_partial_filled = trade_client.get_orders(symbol=symbol, order_state=OrderState.PARTIAL_FILLED,
                                        order_type=None, start_date=None, end_date=None,
                                    start_id=None, size=None, direct=QueryDirection.PREV)
        count=len(list_obj_submitted) + len(list_obj_partial_filled)
    except:
        print("ExecuteError")
        return False, 0
    return True, count

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

def get_orders_id_list(symbol):
    try:
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
        list_obj = trade_client.get_orders(symbol=symbol, order_state=OrderState.SUBMITTED,
                                        order_type=None, start_date=None, end_date=None,
                                    start_id=None, size=None, direct=QueryDirection.PREV)
        order_id_list = []
        if len(list_obj):
            a = __Autonomy__()
            current = sys.stdout
            sys.stdout = a
            LogInfo.output_list(list_obj)
            sys.stdout = current
            order_id_list = get_value("Order Id", a._buff)
    except:
        print("ExecuteError")

    return order_id_list


def get_orders(symbol):
    trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
    list_obj = trade_client.get_orders(symbol=symbol, order_state=OrderState.SUBMITTED,
                                    order_type=None, start_date=None, end_date=None,
                                   start_id=None, size=None, direct=QueryDirection.PREV)
                                    #order_type=OrderType.BUY_LIMIT, start_date=None, end_date=None,

    LogInfo.output("===== {symbol} {count} orders found".format(symbol=symbol, count=len(list_obj)))
    if len(list_obj):
        LogInfo.output_list(list_obj)

def batch_cancel_orders(symbol, order_id_list):
    trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
    print("cancel order list:", order_id_list)
    if len(order_id_list):
        result = trade_client.cancel_orders(symbol, order_id_list)
        result.print_object()


def create_buy_order(symbol, price, amount):
    try:
        account_id = 23455585 
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
        order_id = trade_client.create_order(symbol=symbol, account_id=account_id, order_type=OrderType.BUY_LIMIT, source=OrderSource.API, amount=amount, price=price)
        logger.info("created BUY order id : {id}\n".format(id=order_id))
        return True, 0
    except Exception as e:
        print("ExecuteError:", e)
        max_size = 0
        # if "order-holding-limit-failed" in e:
        #     max_size = re.findall("\d+\.*\d*", e)
        return False, max_size

def create_sell_order(symbol, price, amount):
    try:
        account_id = 23455585 
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
        order_id = trade_client.create_order(symbol=symbol, account_id=account_id, order_type=OrderType.SELL_LIMIT, source=OrderSource.API, amount=amount, price=price)
        logger.info("created SELL order id : {id}\n".format(id=order_id))
        return True
    except Exception as e:
        print("ExecuteError:", e)
        return False

def get_current_price(symbol):
    market_client = MarketClient()
    depth_size = 2
    depth = market_client.get_pricedepth(symbol, DepthStep.STEP0, depth_size)
    #LogInfo.output("---- Top {size} bids ----".format(size=len(depth.bids)))
    i = 0
    for entry in depth.bids:
        i = i + 1
        if i == 1:
            first_price = entry.price
        #LogInfo.output(str(i) + ": price: " + str(entry.price) + ", amount: " + str(entry.amount))
    return first_price


def get_usdt_trade_balance():
    try:
        account_id = 23455585 
        account_client = AccountClient(api_key=g_api_key,
                                secret_key=g_secret_key)
        list_obj = account_client.get_balance(account_id=account_id)
        for balance_obj in list_obj:
            if float(balance_obj.balance) > 0.1:  # only show account with balance
                order_type = []
                a = __Autonomy__()
                current = sys.stdout
                sys.stdout = a
                balance_obj.print_object("\t")
                sys.stdout = current
                order_type = get_value("usdt", a._buff)
                if order_type:
                    #print(order_type)
                    #print(a._buff)
                    order_type = get_value("trade", a._buff)
                    if order_type:
                        #print(order_type)
                        #print(a._buff)
                        order_type = get_value("Balance", a._buff)
                        if order_type:
                            #print(order_type[1])
                            return order_type[1]
    except:
        print("ExecuteError")
    return 0.0 

def get_eth3l_trade_balance():
    account_id = 23455585
    account_client = AccountClient(api_key=g_api_key,
                              secret_key=g_secret_key)
    list_obj = account_client.get_balance(account_id=account_id)
    for balance_obj in list_obj:
        if float(balance_obj.balance) > 0.1:  # only show account with balance
            order_type = []
            a = __Autonomy__()
            current = sys.stdout
            sys.stdout = a
            balance_obj.print_object("\t")
            sys.stdout = current
            order_type = get_value("eth3l", a._buff)
            if order_type:
                #print(order_type)
                #print(a._buff)
                order_type = get_value("trade", a._buff)
                if order_type:
                    #print(order_type)
                    #print(a._buff)
                    order_type = get_value("Balance", a._buff)
                    if order_type:
                        #print(order_type[1])
                        return order_type[1]
    return 0.0 

def print_current_price_buy_sell_state():
    buy_num = 0
    sell_num = 0
    for k,v in state_points.items():
        if v==1:
            print("%.4f  %s"%(k,"BUY"))
        elif v==2:
            print("%.4f  %s  -->  %.4f"%(k,"SELL", k+5))
        if v == 1:
            buy_num = buy_num +1
        elif v == 2:
            sell_num = sell_num +1
    print("buy: %d <---> sell: %d"%(buy_num, sell_num))

def create_my_order(buy_price, sell_price, symbol, each_usdt_amount):
    eth3_bal = float(get_eth3l_trade_balance())
    sell_eth_amount = each_usdt_amount / buy_price
    sell_eth_amount = int(sell_eth_amount*10000)/10000
    current_price = get_current_price(symbol)

    if buy_price in state_points:
        logger.info("last state for %f is %s "%(buy_price, "BUY" if state_points[buy_price]==1 else "SELL" ))
        last_state_price = state_points[buy_price]
    else:
        logger.info("last state for %f is unknown "%(buy_price))
        last_state_price = 0

    if (eth3_bal > sell_eth_amount or eth3_bal>0.2) and sell_price > current_price and last_state_price ==1:
        #only after buy then can sell, so the last state should be 1 if want to sell
        if eth3_bal < sell_eth_amount and eth3_bal>0.2:
            logger.warning("something like less balance now, what happened? maybe deduct fee cause this issue. eth3_bal=%f sell_eth_amount=%f, updated!"%(eth3_bal, sell_eth_amount))
            sell_eth_amount = eth3_bal
        logger.info("There are balacne %f of %s, sell %f at price %f first."%(eth3_bal, symbol, sell_eth_amount, sell_price))
        total_sell_num = int(sell_eth_amount*10000)/10000
        logger.info("Total are %f, create sell %f %s at price %.4f now."%(eth3_bal, total_sell_num, symbol, sell_price))
        ret = create_sell_order(symbol, sell_price, total_sell_num)
        if ret:
            state_points[buy_price] = 2
        return ret

    elif last_state_price != 1 and current_price > buy_price :
        #the first time can use buy, actually any time can use buy, 
        #for it already make sure buy happend when current price > buy_price
        total_usdt = float(get_usdt_trade_balance())

        logger.info("usdt trade balace is %f"%(total_usdt))

        if total_usdt < 1 or total_usdt < each_usdt_amount:
            logger.warning("total usdt is very less, it's %f, can't buy now, please check your usdt balance, current_price=%f, each_usdt_amount=%f"%(total_usdt, current_price, each_usdt_amount))
            return False

        use_usdt = each_usdt_amount

        total_buy_num = int((use_usdt/ buy_price )*10000)/10000
        logger.info("total usdt is %f, use_usdt=%f, buy_price=%.4f, buy_amount=%f"%(total_usdt, use_usdt, buy_price, total_buy_num))

        logger.info("use usdt %f to buy %f %s at price %.4f now..."%(use_usdt, total_buy_num, symbol, buy_price))
        ret, max_size = create_buy_order(symbol, buy_price, total_buy_num)
        if ret:
            state_points[buy_price] = 1
        # else:
        #     if max_size:
        #         logger.warning("retry the order-holding-limit-failed sugguest amount:%f"%float(max_size))
        #         ret, max_size = create_buy_order(symbol, buy_price, float(max_size))
        #         if ret:
        #             state_points[buy_price] = 1
        return ret
    else:
        if current_price < buy_price :
            logger.warning("current_price=%.4f < buy_price=%.4f, it's not good time to buy now."%(current_price, buy_price))
        logger.warning("IF not price is low than buy price, then please have a check, eth3_bal=%f, sell_eth_amount=%f, current_price=%f, buy_price=%.4f, sell_price=%.4f\n"%(eth3_bal, sell_eth_amount, current_price, buy_price, sell_price))

    return False


#fh = logging.FileHandler("log/%s-%s.log"%(symbol, time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())))
#fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
#fh.setFormatter(formatter)
logger.addHandler(ch)
#logger.addHandler(fh)

argnum = len(sys.argv)
if argnum < 4:
    logger.error("please input parameters, range, monitor_num")
    exit(1)

start_point = float(sys.argv[1])
end_point = float(sys.argv[2])
step = float(end_point - start_point +1)/int(sys.argv[3])

for i in range(0, int(sys.argv[3])):
    buy_price_tmp = int((start_point + i*step)*10000)/10000
    price_points.append(buy_price_tmp)

price_points = sorted(price_points, key = lambda x:float(x))

current_price = get_current_price(symbol)
logger.info("current_prince=%f, buy price:%r"%(current_price, price_points))

if argnum == 5:
    total_usdt = float(sys.argv[4])
    each_amount = total_usdt/int(sys.argv[3])

while 1:
    print("\n\n\n")
    current_price = get_current_price(symbol)
    for buy_price in price_points:
        sell_price = buy_price + 5
        logger.info("Handle price %.4f <-- %f (current price)"%(buy_price, current_price))
        execute_result, execute_num = has_orders(symbol)
        if execute_result and execute_num:
            has_exact_order, is_buy = has_buy_order(symbol, buy_price, sell_price, True)
            if has_exact_order and is_buy:
                logger.info("Has BUY order ongoing, %.4f <-- %f (current price) waiting...\n"%(buy_price, current_price))
                state_points[buy_price] = 1
            elif not is_buy and has_exact_order:
                logger.info("Has SELL order ongoing,%.4f <-- %f (current price) waiting...\n"%(sell_price, current_price))
                state_points[buy_price] = 2
            else :
                logger.warning("START to create order, is_buy=%d, buy_price=%.4f, sell_price=%.4f"%(is_buy, buy_price, sell_price))
                created_success = create_my_order(buy_price, sell_price, symbol, each_amount)

        elif execute_result and not execute_num:
            created_success = create_my_order(buy_price, sell_price, symbol, each_amount)

        else:
            logger.info("most probably failed to execute here")

    logger.info("each_amount = %f, current_prince=%f, buy price:%r, Let me sleep for one minute..."%(each_amount, current_price, price_points))

    print_current_price_buy_sell_state()
    print("current price:", current_price)
    logger.info("len(state_points) = %d, len(price_points) = %d"%(len(state_points), len(price_points)))
    price_list = []
    for price in price_points:
        if price not in state_points:
            price_list.append(price)

    if len(price_list):
        print("ISSUE: please check, no state price list:", price_list)
        send_email("HB: " + "ISSUE some price state goes wrong", ','.join('%s' %id for id in price_list))
    print("=======================================================================================================================")
    time.sleep(30)
