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
import threading
import MySQLdb
import queue


symbol = "ethusdt"
price_difference = 50
price_precision = 100 #price 价格精度
amount_precision = 10000

price_points = []
state_points = {}

db = MySQLdb.connect("localhost", "root", "abcd.12345", "ecoin_system", charset='gb2312' )
cursor = db.cursor()

#buy=1, sell=2
def check_order_in_db(symbol, buy_sell, price):
    #print(symbol, buy_sell, price)
    sql = "SELECT * FROM trade_order \
       WHERE symbol='%s' and buy_sell=%d" % (symbol, buy_sell)
    #print(sql)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            id = row[0]
            orderid = row[1]
            #symbol = row[2]
            #buy_sell = row[3]
            db_price = row[4]
            #amount = row[4]
            #print("id=%s, orderid=%s, symbol=%s, buy_sell=%s, price=%s, amount=%s" % \
            #        (id, orderid, symbol, buy_sell, price, amount))
            if price == db_price:
                return orderid
    except:
        #print("Error: unable to fecth data")
        return 0

def insert_into_db(orderid, symbol, buy_sell, price, amount):
    #print(orderid, symbol, buy_sell, price, amount)
    sql = "INSERT INTO trade_order(orderid, \
            symbol, buy_sell, price, amount) \
            VALUES (%d, '%s', %f, %f, %f)"% (orderid, symbol, buy_sell, price, amount)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

def remove_order_in_db(orderid):
    #print(orderid, symbol, buy_sell, price, amount)
    sql = "deleteorderid from trade_order \
            where orderid=%d)"% (orderid)
    try:
        cursor.execute(sql)
        db.commit()
        printme("order id %d is removed from local db"%(total_usdt))
    except:
        db.rollback()




def printme( str ):
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    print(cur_time+ str)  #logger.info

def printme_error( str ):
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    print(cur_time+ str)  #logger.error

def printme_warning( str ):
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    print(cur_time+ str)  #logger.warning


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
            order_id = get_value("Order Id", a._buff)
            amount = get_value("Amount", a._buff)
            price = get_value("Price", a._buff)
            current_price =float(price[0]) 
            if (order_type[0] == "buy-limit"):
                if current_price == buy_price:
                    return True,True,int(order_id[0]),float(amount[0])
            else:
                if current_price == sell_price:
                    return True,False,int(order_id[0]),float(amount[0])
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
                order_id = get_value("Order Id", a._buff)
                amount = get_value("Amount", a._buff)
                price = get_value("Price", a._buff)
                current_price =float(price[0]) 
                if (order_type[0] == "buy-limit"):
                    if current_price == buy_price:
                        return True,True,int(order_id[0]),float(amount[0])
                else:
                    if current_price == sell_price:
                        return True,False,int(order_id[0]),float(amount[0])
        except:
            print("ExecuteError")
    return False,False,0,0

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
        printme("created BUY order id : {id}\n".format(id=order_id))
        return True, order_id, 0
    except Exception as e:
        print("ExecuteError:", e)
        max_size = 0
        # if "order-holding-limit-failed" in e:
        #     max_size = re.findall("\d+\.*\d*", e)
        return False, 0, max_size

def create_sell_order(symbol, price, amount):
    try:
        account_id = 23455585 
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
        order_id = trade_client.create_order(symbol=symbol, account_id=account_id, order_type=OrderType.SELL_LIMIT, source=OrderSource.API, amount=amount, price=price)
        printme("created SELL order id : {id}\n".format(id=order_id))
        return True, order_id
    except Exception as e:
        print("ExecuteError:", e)
        return False, 0

def get_current_price(symbol):
    try:
        market_client = MarketClient()
        depth_size = 2
        depth = market_client.get_pricedepth(symbol, DepthStep.STEP0, depth_size)
        #LogInfo.output("---- Top {size} bids ----".format(size=len(depth.bids)))
        i = 0
        for entry in depth.bids:
            i = i + 1
            if i == 1:
                first_price = entry.price
                return first_price
            #LogInfo.output(str(i) + ": price: " + str(entry.price) + ", amount: " + str(entry.amount))
    except Exception as e:
        print("ExecuteError:", e)
        return 0


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
            print("%.4f  %s  -->  %.4f"%(k,"SELL", k+price_difference))
        if v == 1:
            buy_num = buy_num +1
        elif v == 2:
            sell_num = sell_num +1
    print("buy: %d <---> sell: %d"%(buy_num, sell_num))

def create_my_order(buy_price, sell_price, symbol, each_usdt_amount):
    eth3_bal = float(get_eth3l_trade_balance())
    sell_eth_amount = each_usdt_amount / buy_price
    sell_eth_amount = int(sell_eth_amount*amount_precision)/amount_precision
    current_price = get_current_price(symbol)

    orderid_sell = check_order_in_db(symbol, 2, sell_price)
    orderid_buy = check_order_in_db(symbol, 1, buy_price)
    if orderid_sell:
        printme_warning("in local db, last state is sell, order id is %d!"% (orderid_sell))
        state_points[buy_price] = 2
        last_state_price = 2
    elif orderid_buy:
        printme_warning("in local db, last state is buy, order id is %d!"% (orderid_buy))
        state_points[buy_price] = 1
        last_state_price = 1
    else:
        last_state_price = 0

    if (eth3_bal > sell_eth_amount or eth3_bal>0.2) and sell_price > current_price and last_state_price ==1:
        #only after buy then can sell, so the last state should be 1 if want to sell
        if eth3_bal < sell_eth_amount and eth3_bal>0.2:
            printme_warning("something like less balance now, what happened? maybe deduct fee cause this issue. eth3_bal=%f sell_eth_amount=%f, updated!"%(eth3_bal, sell_eth_amount))
            sell_eth_amount = eth3_bal
        printme("There are balacne %f of %s, sell %f at price %f first."%(eth3_bal, symbol, sell_eth_amount, sell_price))
        total_sell_num = int(sell_eth_amount*amount_precision)/amount_precision
        printme("Total are %f, create sell %f %s at price %.4f now."%(eth3_bal, total_sell_num, symbol, sell_price))
        ret, order_id = create_sell_order(symbol, sell_price, total_sell_num)
        if ret:
            state_points[buy_price] = 2
            if orderid_buy:
                remove_order_in_db(orderid_buy)

        return ret, 2, order_id, total_sell_num

    elif last_state_price != 1 and current_price > buy_price :
        #the first time can use buy, actually any time can use buy, 
        #for it already make sure buy happend when current price > buy_price
        total_usdt = float(get_usdt_trade_balance())

        printme("usdt trade balace is %f"%(total_usdt))

        if total_usdt < 1 or total_usdt < each_usdt_amount:
            printme_warning("total usdt is very less, it's %f, can't buy now, please check your usdt balance, current_price=%f, each_usdt_amount=%f"%(total_usdt, current_price, each_usdt_amount))
            return False, 0,0,0

        use_usdt = each_usdt_amount

        total_buy_num = int((use_usdt/ buy_price )*amount_precision)/amount_precision
        printme("total usdt is %f, use_usdt=%f, buy_price=%.4f, buy_amount=%f"%(total_usdt, use_usdt, buy_price, total_buy_num))

        printme("use usdt %f to buy %f %s at price %.4f now..."%(use_usdt, total_buy_num, symbol, buy_price))
        ret, order_id, max_size = create_buy_order(symbol, buy_price, total_buy_num)
        if ret:
            state_points[buy_price] = 1
            if orderid_sell:
                remove_order_in_db(orderid_sell)
        # else:
        #     if max_size:
        #         printme_warning("retry the order-holding-limit-failed sugguest amount:%f"%float(max_size))
        #         ret, max_size = create_buy_order(symbol, buy_price, float(max_size))
        #         if ret:
        #             state_points[buy_price] = 1
        return ret, 1, order_id, total_buy_num
    else:
        if buy_price in state_points:
            state_points.pop(buy_price)
        if current_price < buy_price :
            printme_warning("current_price=%.4f < buy_price=%.4f, it's not good time to buy now."%(current_price, buy_price))
        printme_warning("IF not price is low than buy price, then please have a check, eth3_bal=%f, sell_eth_amount=%f, current_price=%f, buy_price=%.4f, sell_price=%.4f\n"%(eth3_bal, sell_eth_amount, current_price, buy_price, sell_price))

    return False,0,0,0

def update_order_implement(trigger):
    print("\n\n\n")
    print("=======================================================================================================================")


def handle_order_update(upd_event: 'OrderUpdateEvent'):
    update_order_implement("Event")

def loop_handle(self):
    while 1:
        update_order_implement("Loop")
        time.sleep(20)

def error_handler(exception: 'HuobiApiException'):
    send_email("HB: " + "subscribe error happened", exception)


class myLoopHandle(threading.Thread):
    def __init__(self, threadID, name, each_amount):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.each_amount = each_amount
    def run(self):
        loop_handle(self)

class myEventHandle(threading.Thread):
    def __init__(self, threadID, name, each_amount):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.each_amount = each_amount

    def run(self):
        #trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key, init_log=True)
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key, init_log=False)
        trade_client.sub_order_update("eth3lusdt,dogeusdt,ethusdt", handle_order_update)

def put_into_queue(q, value):
    if q.qsize() >= 5:
        q.get()
        q.put(value)
    else:
        q.put(value)

def order_even_value(q):
    last_item_min = 0
    last_item_max = 99999999
    inc_flag = True
    dec_flag = True
    total = 0

    i = 1
    for q_item in q.queue:
        if i == 1:
            first_item = q_item
        elif i == q.qsize():
            last_item = q_item

        if q.qsize() >= 3:
            if last_item_min <= q_item and inc_flag:
                last_item_min = q_item
            else:
                inc_flag = False

            if last_item_max >= q_item and dec_flag:
                last_item_max = q_item
            else:
                dec_flag = False
        else:
            dec_flag = False
            inc_flag = False
        total = total + q_item
        i = i + 1

    e_value = int(total *1000 / q.qsize())/1000
    if inc_flag:
        order = 1
        diff = last_item - first_item
    elif dec_flag:
        order = 2
        diff = first_item - last_item
    else:
        order = 0
        diff = 0

    return order, e_value, diff

def output_to_log_file(fp, string):
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    fp.write(cur_time + string+"\n")
    printme(string)
    fp.flush()

if __name__ == '__main__':

    cur_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    log_file = "log/auto-hunter-%s.txt"%cur_time
    f_res = open(log_file, mode='w')
    print("tail -f "+log_file)

    q = queue.Queue()
    q_price_list = []
    eq_price_list = []
    eq = queue.Queue()

    q_buy_price = 0
    q_sell_price = 0

    eq_buy_price = 0
    eq_sell_price = 0

    steps_dec = 10
    q_accu_dec = 0
    eq_accu_dec = 0

    steps_inc = 10
    q_accu_inc = 0
    eq_accu_inc = 0

    diff_space = 30
    deal_space = 50  # sell out if the space reach 50?

    while (1):
        current_price = get_current_price(symbol)
        if current_price == 0:
            time.sleep(1)
            continue

        put_into_queue(q, current_price)


        q_order, q_even, q_diff = order_even_value(q)
        put_into_queue(eq, q_even)
        eq_order, eq_even, eq_diff = order_even_value(eq)

        qstr = ""
        if q_order == 1:
            if q_buy_price:
                qstr += "Q is ++ diff:%.2f %.2f"%(q_diff,current_price-q_buy_price)
            else:
                qstr += "Q is ++ diff:%.2f"%(q_diff)
            q_accu_inc = q_accu_inc +1
            if q_accu_dec >= steps_dec and (q_buy_price > current_price + diff_space or q_buy_price==0):
                q_buy_price = current_price
                q_price_list.append(q_buy_price)
                output_to_log_file(f_res, "BUY/Q: %f, %r"%(current_price, q_price_list))
            if q_accu_inc >= 2:
                q_accu_dec = 0

        elif q_order == 2:
            if q_buy_price:
                qstr += "Q is -- diff:%.2f  %.2f"%(q_diff,current_price-q_buy_price)
            else:
                qstr += "Q is -- diff:%.2f"%(q_diff)
            q_accu_dec = q_accu_dec +1
            if q_accu_inc >= steps_inc and (current_price-q_buy_price) > diff_space and q_buy_price:
                q_price_list.pop()
                output_to_log_file(f_res, "SELL/Q: %f, buy:%f diff:%f"%(current_price, q_buy_price, current_price-q_buy_price))
                if len(q_price_list):
                    q_buy_price = q_price_list[len(q_price_list)-1]
                else:
                    q_buy_price = 0
                q_sell_price = current_price

            if q_accu_dec >= 2:
                q_accu_inc = 0
        else:
            if current_price - q_buy_price > deal_space and q_buy_price:
                q_price_list.pop()
                output_to_log_file(f_res, "SELL/Q: %f, deal_space=%f buy:%f diff:%f"%(current_price, deal_space, q_buy_price, current_price-q_buy_price))
                if len(q_price_list):
                    q_buy_price = q_price_list[len(q_price_list)-1]
                else:
                    q_buy_price = 0
                q_sell_price = current_price

        eqstr = ""
        if eq_order == 1:
            if eq_buy_price:
                eqstr += "EQ is ++ diff:%.2f  %.2f"%(eq_diff,current_price-eq_buy_price)
            else:
                eqstr += "EQ is ++ diff:%.2f"%(eq_diff)
            eq_accu_inc = eq_accu_inc +1
            if eq_accu_dec >= steps_dec and (eq_buy_price > current_price + diff_space or eq_buy_price==0):
                eq_buy_price = current_price
                eq_price_list.append(eq_buy_price)
                output_to_log_file(f_res, "BUY/EQ: %f, %r"%(current_price, eq_price_list))
            if eq_accu_inc >= 2:
                eq_accu_dec = 0

        elif eq_order == 2:
            if eq_buy_price:
                eqstr += "EQ is -- diff:%.2f %.2f"%(eq_diff,current_price-eq_buy_price)
            else:
                eqstr += "EQ is -- diff:%.2f"%(eq_diff)
            eq_accu_dec = eq_accu_dec +1
            if eq_accu_inc >= steps_inc and (current_price-eq_buy_price) > diff_space and eq_buy_price:
                eq_price_list.pop()
                output_to_log_file(f_res, "SELL/EQ: %f, buy:%f diff:%f"%(current_price, eq_buy_price, current_price-eq_buy_price))
                if len(eq_price_list):
                    eq_buy_price = eq_price_list[len(eq_price_list)-1]
                else:
                    eq_buy_price = 0
                eq_sell_price = current_price

            if eq_accu_dec >= 2:
                eq_accu_inc = 0
        else:
            if current_price-eq_buy_price > deal_space and eq_buy_price:
                eq_price_list.pop()
                output_to_log_file(f_res, "SELL/EQ: %f, deal_space=%f buy:%f diff:%f"%(current_price, deal_space, eq_buy_price, current_price-eq_buy_price))
                if len(eq_price_list):
                    eq_buy_price = eq_price_list[len(eq_price_list)-1]
                else:
                    eq_buy_price = 0
                eq_sell_price = current_price


        if qstr or eqstr:
            printme("cur_price=%.2f, q_accu_dec/q_accu_inc=%d/%d %s %r"%(current_price, q_accu_dec, q_accu_inc, qstr, q_price_list))
            printme("cur_price=%.2f, eq_accu_dec/eq_accu_inc=%d/%d %s %r"%(current_price, eq_accu_dec, eq_accu_inc, eqstr, eq_price_list))
        #if qstr or eqstr:
        printme("===============================================================================================\n")
        time.sleep(3)



