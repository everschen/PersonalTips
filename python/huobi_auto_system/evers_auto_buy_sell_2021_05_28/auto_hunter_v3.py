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
import getopt


symbol = "ethusdt"
price_difference = 50
price_precision = 100 #price 价格精度
amount_precision = 10000
db_program_id = 1
loop_time = 3  #seconds
ORDER_TIMEOUT_LOOP_TIMES = int(5*60/loop_time)  #5 minutes
JUST_BUY_TIME = 120  #6 minutes



buy_order_ongoing = False
sell_order_ongoing = False
lock = threading.Lock()

db = MySQLdb.connect("localhost", "root", "abcd.12345", "ecoin_system", charset='gb2312' )
cursor = db.cursor()

#buy=1, sell=2
def check_order_in_db(symbol, buy_sell, price, db_program_id):
    cursor = db.cursor()
    #print(symbol, buy_sell, price)
    sql = "SELECT * FROM trade_order \
       WHERE symbol='%s' and buy_sell=%d and program=%d" % (symbol, buy_sell, db_program_id)
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

def insert_into_db(orderid, symbol, buy_sell, price, amount, db_program_id):
    cursor = db.cursor()
    sql = "INSERT INTO trade_order(orderid, \
            symbol, buy_sell, price, amount, program) \
            VALUES (%d, '%s', %d, %f, %f, %d)"% (orderid, symbol, buy_sell, price, amount, db_program_id)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

def remove_order_in_db(orderid):
    sql = "delete from trade_order where orderid=%d"%(orderid)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
        printme("order id %d is removed from local db"%(orderid))
    except:
        printme("failed to remove orderid:%d"%(orderid))
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
        printme("created BUY order id : %d price=%.2f, amount=%f\n"%(order_id, price, amount))
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

def get_trade_balance(bal_name):
    account_id = 23455585
    account_client = AccountClient(api_key=g_api_key,
                              secret_key=g_secret_key)
    list_obj = account_client.get_balance(account_id=account_id)
    for balance_obj in list_obj:
        if float(balance_obj.balance) > 0.0001:  # only show account with balance
            order_type = []
            a = __Autonomy__()
            current = sys.stdout
            sys.stdout = a
            balance_obj.print_object("\t")
            sys.stdout = current
            #order_type = get_value("eth", a._buff, True)
            order_type = get_value(bal_name, a._buff)
            #print("t", order_type)
            if len(order_type) and order_type[0] == bal_name:
                #print(order_type)
                #print(a._buff)
                order_type = get_value("trade", a._buff)
                #print(order_type)
                if order_type:
                    #print(order_type)
                    #print(a._buff)
                    order_type = get_value("Balance", a._buff)
                    if order_type:
                        #print(order_type[1])
                        return order_type[1]
    return 0.0 

def update_order_implement(trigger):
    print("\n\n\n")
    print("=======================================================================================================================")

def get_first_value(list_value):
    if len(list_value):
        ret = list_value[0].strip()
    else:
        ret=""
    return ret

def handle_order_id(order_id, order_type, price):
    lock.acquire()
    global buy_order_ongoing
    global sell_order_ongoing
    global price_list
    global f_trade_done
    global just_buy_time_out # 6 minutes
    print("start to handle order id %d now"%order_id)
    if order_type=="sell-limit":
        buy_price  = get_previous_price(price_list)
        if len(price_list):
            price_list.pop()
        remove_order_in_db(order_id)
        output_to_log_file(f_trade_done, "SELL done: %.2f, buy:%.2f diff:%.2f \n"%(price, buy_price, price-buy_price))
        sell_order_ongoing = False
        just_buy_time_out = 0
    elif order_type=="buy-limit":
        remove_order_in_db(order_id)
        price_list.append(price)
        output_to_log_file(f_trade_done, "BUY done: %.2f, %r \n"%(price, price_list))
        buy_order_ongoing = False
        just_buy_time_out = JUST_BUY_TIME

    else:
        print("sth wrong? order_type=%s"%order_type)
    lock.release()

def handle_order_update(upd_event: 'OrderUpdateEvent'):
    try:
        print("handle order update now...")
        b = __Autonomy__()
        current = sys.stdout
        sys.stdout = b
        upd_event.print_object()
        sys.stdout = current

        order_type = get_value("Order Type", b._buff)
        order_id = get_value("Order Id", b._buff)
        price = get_value("Trade Price", b._buff)
        order_state = get_value("Order State", b._buff)
        amount = get_value("Trade Volume", b._buff)

        if get_first_value(order_state) != "filled":
            return

        order_type = get_first_value(order_type)
        order_state = get_first_value(order_state)
        price = float(get_first_value(price))
        order_id = int(get_first_value(order_id))
        amount = float(get_first_value(amount))

        print("order_state=", order_state)
        print("order_type=", order_type)
        print("price=", price)
        print("order_id=", order_id)
        print("amount=", amount)


        handle_order_id(order_id, order_type, price)

    except Exception as e:
        print("ExecuteError in handle_order_update", e)

def cancel_order_and_restore_system(symbol, orderid):
    order_list = []
    order_list.append(orderid)
    batch_cancel_orders(symbol, order_list)
    remove_order_in_db(orderid)

def sell_policy_analyse(f_trade_done, inc_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val,diff_space_buy,usdt_amount,accu_buy_val, accu_buy, price_list):
    output_to_log_file(f_trade_done, "sell %.2f Q analyse: ===================start=================="%(current_price), True)
    output_to_log_file(f_trade_done, "sell %.2f Q analyse: times:%d/%d diff:%.2f"%(current_price, already_buy_times, total_buy_times, current_price-buy_price))
    output_to_log_file(f_trade_done,"Q --%d/++%d %s %r"%(q_accu_dec, q_accu_inc, qstr, q.queue))
    output_to_log_file(f_trade_done,"EQ --%d/++%d %s %r"%(eq_accu_dec, eq_accu_inc, eqstr, eq.queue))
    if big_drop_flag:
        output_to_log_file(f_trade_done,"BIGDROP:%d %sgap:%s sell/deal=%.2f(%.3f%%)/%.2f(%.3f%%) buy_space=%.2f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))
    else:
        output_to_log_file(f_trade_done,"%sgap:%s sell/deal=%.2f(%.3f%%)/%.2f(%.3f%%) buy_space=%.2f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))

    output_to_log_file(f_trade_done,"inc:%.2f accu_buy:%.2f/%.2f%% price list: %r"%(current_price-inc_start, accu_buy_val, accu_buy, price_list))
    output_to_log_file(f_trade_done, "sell %.2f Q analyse: ===================end==================="%(current_price))

def buy_policy_analyse(f_trade_done, q_accu_dec_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq, big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list):
    output_to_log_file(f_trade_done, "buy %.2f Q analyse: ===================start=================="%(current_price), True)
    output_to_log_file(f_trade_done, "buy %.2f Q analyse: times:%d/%d diff:%.2f"%(current_price, already_buy_times, total_buy_times, buy_price - current_price))
    output_to_log_file(f_trade_done,"Q --%d/++%d %s %r"%(q_accu_dec, q_accu_inc, qstr, q.queue))
    output_to_log_file(f_trade_done,"EQ --%d/++%d %s %r"%(eq_accu_dec, eq_accu_inc, eqstr, eq.queue))
    if big_drop_flag:
        output_to_log_file(f_trade_done,"BIGDROP:%d %sgap:%s sell/deal=%.2f(%.3f%%)/%.2f(%.3f%%) buy_space=%.2f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))
    else:
        output_to_log_file(f_trade_done,"%sgap:%s sell/deal=%.2f(%.3f%%)/%.2f(%.3f%%) buy_space=%.2f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))

    output_to_log_file(f_trade_done,"dec:%.2f accu_buy:%.2f/%.2f%% price list: %r"%(q_accu_dec_start-current_price, accu_buy_val, accu_buy, price_list))
    output_to_log_file(f_trade_done, "buy %.2f Q analyse: ===================end==================="%(current_price))

def loop_handle():
    q = queue.Queue()
    eq = queue.Queue()

    steps_dec = 10
    q_accu_dec = 0
    eq_accu_dec = 0

    steps_inc = 10
    q_accu_inc = 0
    eq_accu_inc = 0
    q_accu_inc_start = 0
    eq_accu_inc_start = 0

    buying = 0
    selling = 0
    order_timeout_checking = 0
    big_change_threhold = 0.6  # 0.6% in 12 seconds
    last_several_times_restrict = 2
    big_drop_flag = False
    big_drop_flag_time_out = 0

    global diff_space_buy
    global diff_space_sell
    global deal_space
    global accu_buy

    global usdt_amount
    global price_list
    global buy_order_ongoing
    global sell_order_ongoing
    global f_trade_done
    global total_buy_times
    global just_buy_time_out

    cur_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    log_file = "log/auto-hunter-price-big-change-%s.txt"%cur_time
    f_price_big_change = open(log_file, mode='w')

    while (1):
        lock.acquire()
        current_price = get_current_price(symbol)
        if current_price == 0:
            time.sleep(1)
            continue

        buy_price  = get_previous_price(price_list)

        if buy_price !=0:
            cal_price = buy_price
        else:
            cal_price = current_price

        diff_space_sell_val = diff_space_sell*cal_price/100
        deal_space_val = deal_space*cal_price/100
        diff_space_buy_val = diff_space_buy*cal_price/100
        accu_buy_val = accu_buy*cal_price/100

        already_buy_times = len(price_list)

        put_into_queue(q, current_price)
        q_order, q_even, q_diff = order_even_value(q)

        put_into_queue(eq, q_even)
        eq_order, eq_even, eq_diff = order_even_value(eq)

        big_change_str = ""
        showgap = ""
        qstr=""
        eqstr=""
        q_diff_percent = q_diff *100 /q_even
        eq_diff_percent = eq_diff *100/eq_even

        if big_drop_flag:
            if big_drop_flag_time_out:
                big_drop_flag_time_out = big_drop_flag_time_out -1
            else:
                big_drop_flag = False

        if just_buy_time_out>0:
            just_buy_time_out = just_buy_time_out -1

        if q_diff_percent > big_change_threhold:
            big_change_str = "Q-UPUPUP %.2f%% "%(q_diff_percent)
            output_to_log_file(f_price_big_change, "Q-UPUPUP: %.2f%%, eq_even:%.2f, q_diff=%.2f"%(q_diff_percent, q_even, q_diff))
            big_drop_flag = False
        elif q_diff_percent < -big_change_threhold:
            big_change_str = "Q-DOWNDOWN %.2f%% "%(q_diff_percent)
            big_drop_flag = True
            big_drop_flag_time_out = 30
            output_to_log_file(f_price_big_change, "Q-DOWNDOWN: %.2f%%, eq_even:%.2f, q_diff=%.2f"%(q_diff_percent, q_even, q_diff))

        if eq_diff_percent > big_change_threhold:
            big_change_str += "EQ-UPUPUP %.2f%% "%(eq_diff_percent)
            output_to_log_file(f_price_big_change, "EQ-UPUPUP: %.2f%%, eq_even:%.2f, q_diff=%.2f"%(eq_diff_percent, eq_even, eq_diff))
            big_drop_flag = False
        elif eq_diff_percent < -big_change_threhold:
            big_change_str += "EQ-DOWNDOWN %.2f%% "%(eq_diff_percent)
            big_drop_flag = True
            big_drop_flag_time_out = 30
            output_to_log_file(f_price_big_change, "EQ-DOWNDOWN: %.2f%%, eq_even:%.2f, q_diff=%.2f"%(eq_diff_percent, eq_even, eq_diff))

        if buy_order_ongoing:
            orderid = check_order_in_db(symbol, 1, buying, 1)
            if not orderid:
                buy_order_ongoing = False
            else:
                if order_timeout_checking > 1 :
                    order_timeout_checking = order_timeout_checking -1
                else:
                    order_timeout_checking = 0
                    printme("canceling buy order id %d"%orderid)
                    cancel_order_and_restore_system(symbol, orderid)
                    buy_order_ongoing = False
                    buying = 0

        if sell_order_ongoing:
            orderid = check_order_in_db(symbol, 2, selling, 1)
            if not orderid:
                sell_order_ongoing = False
            else:
                if order_timeout_checking > 1 :
                    order_timeout_checking = order_timeout_checking -1
                else:
                    order_timeout_checking = 0
                    printme("canceling sell order id %d"%orderid)
                    cancel_order_and_restore_system(symbol, orderid)
                    sell_order_ongoing = False
                    selling = 0

        if q_order == 1:
            q_accu_inc = q_accu_inc +1
            if q_accu_inc == 1:
                q_accu_inc_start = get_last_second_value(q)
            elif q_accu_inc == 0:
                q_accu_inc_start = current_price
            qstr = "Q is ++ adiff:%.2f Qdiff:%.2f %.2f%%"%(current_price-q_accu_inc_start, q_diff, q_diff_percent)

            if just_buy_time_out == 0 and q_accu_dec_start-current_price > accu_buy_val and already_buy_times < total_buy_times and not buy_order_ongoing and q_accu_dec >= steps_dec and (buy_price > current_price + diff_space_buy_val or buy_price==0):
                if (already_buy_times + last_several_times_restrict >= total_buy_times and big_drop_flag) or already_buy_times + last_several_times_restrict < total_buy_times:
                    ret = handle_buy_order(symbol, current_price, usdt_amount)
                    if ret:
                        buy_order_ongoing = True
                        buying = current_price
                        order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                        buy_policy_analyse(f_trade_done, q_accu_dec_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)
                elif already_buy_times + last_several_times_restrict >= total_buy_times and not big_drop_flag:
                    output_to_log_file(f_trade_done, "CANCEL Q buy for last times %d/%d, no big drop. cur_price:%.2f diff:%.2f"%(already_buy_times, total_buy_times, current_price, buy_price - current_price))


            if q_accu_inc >= 2:
                q_accu_dec = 0

        elif q_order == 2:
            q_accu_dec = q_accu_dec +1
            if q_accu_dec == 1:
                q_accu_dec_start = get_last_second_value(q)
            elif q_accu_dec == 0:
                q_accu_dec_start = current_price
            qstr = "Q is -- adiff:%.2f Qdiff:%.2f %.2f%%"%(current_price-q_accu_dec_start, q_diff, q_diff_percent)

            if not sell_order_ongoing and current_price-buy_price > diff_space_sell_val and buy_price:
                ret = handle_sell_order(symbol, current_price, usdt_amount)
                if ret:
                    sell_order_ongoing = True
                    selling = current_price
                    order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                    sell_policy_analyse(f_trade_done, q_accu_inc_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)
            if q_accu_dec >= 2:
                q_accu_inc = 0
        else:
            qstr = "        Qdiff:%.2f %.2f%%"%(q_diff, q_diff_percent)
            if not sell_order_ongoing and current_price - buy_price > deal_space_val and buy_price:
                ret = handle_sell_order(symbol, current_price, usdt_amount)
                if ret:
                    sell_order_ongoing = True
                    selling = current_price
                    order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                    if eq_accu_inc_start > q_accu_inc_start:
                        inc_start = eq_accu_inc_start
                    else:
                        inc_start = q_accu_inc_start
                    sell_policy_analyse(f_trade_done, inc_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)

        if eq_order == 1:
            eq_accu_inc = eq_accu_inc +1
            if eq_accu_inc == 1:
                eq_accu_inc_start = get_last_second_value(q)
            elif eq_accu_inc == 0:
                eq_accu_inc_start = current_price

            eqstr = "EQ is ++ adiff:%.2f EQdiff:%.2f %.2f%%" %(current_price-eq_accu_inc_start, eq_diff, eq_diff_percent)

            if just_buy_time_out == 0 and eq_accu_dec_start-current_price > accu_buy_val and already_buy_times < total_buy_times and not buy_order_ongoing and eq_accu_dec >= steps_dec and (buy_price > current_price + diff_space_buy_val or buy_price==0):
                if (already_buy_times + last_several_times_restrict >= total_buy_times and big_drop_flag) or already_buy_times + last_several_times_restrict < total_buy_times:
                    ret = handle_buy_order(symbol, current_price, usdt_amount)
                    if ret:
                        buy_order_ongoing = True
                        buying = current_price
                        order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                        buy_policy_analyse(f_trade_done, q_accu_dec_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)
                elif already_buy_times + last_several_times_restrict >= total_buy_times and not big_drop_flag:
                    output_to_log_file(f_trade_done, "CANCEL EQ buy for last times %d/%d, no big drop. cur_price:%.2f diff:%.2f"%(already_buy_times, total_buy_times, current_price, buy_price - current_price))


            if eq_accu_inc >= 2:
                eq_accu_dec = 0

        elif eq_order == 2:
            eq_accu_dec = eq_accu_dec +1
            if eq_accu_dec == 1:
                eq_accu_dec_start = get_last_second_value(q)
            elif eq_accu_dec == 0:
                eq_accu_dec_start = current_price
            eqstr = "EQ is -- adiff:%.2f EQdiff:%.2f %.2f%%"%(current_price-eq_accu_dec_start, eq_diff, eq_diff_percent)

            if not sell_order_ongoing and (current_price-buy_price) > diff_space_sell_val and buy_price:
                ret = handle_sell_order(symbol, current_price, usdt_amount)
                if ret:
                    sell_order_ongoing = True
                    selling = current_price
                    order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                    sell_policy_analyse(f_trade_done, eq_accu_inc_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)

            if eq_accu_dec >= 2:
                eq_accu_inc = 0
        else:
            eqstr = "         EQdiff:%.2f %.2f%%"%(eq_diff, eq_diff_percent)
            if not sell_order_ongoing and current_price-buy_price > deal_space_val and buy_price:
                ret = handle_sell_order(symbol, current_price, usdt_amount)
                if ret:
                    sell_order_ongoing = True
                    selling = current_price
                    order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                    if eq_accu_inc_start > q_accu_inc_start:
                        inc_start = eq_accu_inc_start
                    else:
                        inc_start = q_accu_inc_start
                    sell_policy_analyse(f_trade_done, inc_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)

        showgap = ""
        if buy_price:
            showgap = "%.2f"%(current_price-buy_price)

        if buy_order_ongoing:
            printme("buying %.2f"%buying)
        if sell_order_ongoing:
            printme("selling %.2f"%selling)
        if qstr or eqstr:
            printme("cur_price=%.2f, --%d/++%d %s %r"%(current_price, q_accu_dec, q_accu_inc, qstr, q.queue))
            printme("cur_price=%.2f, --%d/++%d %s %r"%(current_price, eq_accu_dec, eq_accu_inc, eqstr, eq.queue))
        else:
            printme("cur_price=%.2f"%(current_price))
        
        if big_drop_flag:
            printme("BIGDROP:%d %sgap:%s sell/deal=%.2f(%.3f%%)/%.2f(%.3f%%) buy_space=%.2f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))
        else:
            printme("%sgap:%s sell/deal=%.2f(%.3f%%)/%.2f(%.3f%%) buy_space=%.2f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))

        printme("buy_timeout:%d accu_buy:%.2f/%.2f%% price list: %r"%(just_buy_time_out, accu_buy_val, accu_buy, price_list))
        #if qstr or eqstr:
        printme("==================================================================================================================\n")
        lock.release()
        time.sleep(loop_time)

def error_handler(exception: 'HuobiApiException'):
    send_email("HB: " + "subscribe error happened", exception)


def myEventHandle():
        #trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key, init_log=True)
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key, init_log=False)
        trade_client.sub_order_update("eth3lusdt,dogeusdt,ethusdt", handle_order_update)

def put_into_queue(q, value):
    if q.qsize() >= 5:
        q.get()
        q.put(value)
    else:
        q.put(value)

def get_last_second_value(q):
    i = 1
    for q_item in q.queue:
        if i == q.qsize()-1:
            last_second_item = q_item
            return last_second_item
        i = i + 1

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
            last_item = q_item
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
        #diff = last_item - first_item
    elif dec_flag:
        order = 2
        #diff = first_item - last_item
    else:
        order = 0

    diff = last_item - first_item

    return order, e_value, diff

def output_to_log_file(fp, string, start_blank=False):
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    if start_blank:
        fp.write("\n" + cur_time + string+"\n")
    else:
        fp.write(cur_time + string+"\n")
    printme(string)
    fp.flush()

def handle_buy_order(symbol, price, usdt_amount):
    price = int( price*price_precision)/price_precision
    usdt_bal = float(get_trade_balance("usdt"))
    if usdt_amount > usdt_bal:
        printme_warning("usdt balance is %f, less than required value %f !"% (usdt_bal, usdt_amount))
        return False
    total_num = int((usdt_amount/ price )*amount_precision)/amount_precision
    ret, order_id, max_size = create_buy_order(symbol, price, total_num)
    if ret:
        insert_into_db(order_id, symbol, 1, price, total_num, db_program_id)
        printme_warning("creatd order id %s in local db!"% (order_id))
    return ret

def handle_sell_order(symbol, price, usdt_amount):
    price = int( price*price_precision)/price_precision
    total_num = int((usdt_amount/ price )*amount_precision)/amount_precision
    eth_bal = float(get_trade_balance("eth"))
    eth_bal = int(eth_bal*amount_precision)/amount_precision
    if eth_bal < total_num:
        total_num = eth_bal
    ret, order_id = create_sell_order(symbol, price, total_num)
    if ret:
        insert_into_db(order_id, symbol, 2, price, total_num, db_program_id)
        printme_warning("creatd order id %s in local db!"% (order_id))
    return ret

def get_previous_price(price_list):
    if len(price_list):
        buy_price = price_list[len(price_list)-1]
    else:
        buy_price = 0
    return buy_price


if __name__ == '__main__':
    price_list = []
    usdt_amount = 20
    diff_space_buy = 1.2   #1.2%
    diff_space_sell = 1 #1%
    deal_space = 1.667  #1.667%
    total_buy_times = 10
    accu_buy = 0.4 #0.4%
    just_buy_time_out = 0
    help_str = "auto_hunter_v2.py -b <diff_space_buy %> -a <accu_buy % > -s <diff_space_sell % > -d <deal_space % > -u <usdt_amount> -p <price_list> -t <total_buy_times>"

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hb:s:d:u:p:t:a:",["help", "diff_space_buy=","accu_buy=","diff_space_sell=","deal_space=","usdt_amount=","price_list=","total_buy_times="])
    except getopt.GetoptError:
        print(help_str)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_str)
            sys.exit(1)
        elif opt in ("-b", "--diff_space_buy"):
            diff_space_buy = float(arg)
        elif opt in ("-a", "--accu_buy"):
            accu_buy = float(arg)
        elif opt in ("-s", "--diff_space_sell"):
            diff_space_sell = float(arg)
        elif opt in ("-d", "--deal_space"):
            deal_space = float(arg)
        elif opt in ("-u", "--usdt_amount"):
            usdt_amount = int(arg)
        elif opt in ("-t", "--total_buy_times"):
            total_buy_times = int(arg)
            if total_buy_times==0:
                total_buy_times = 999999999
        elif opt in ("-p", "--price_list"):
            input_str = arg
            if input_str.strip() != "":
                if input_str[0] == '[' and input_str[-1]== ']':
                    input_str = input_str[1:(len(input_str)-1)]
                input_str = input_str.split(",")
                result = []
                for item in input_str:
                    result.append(float(item))
                price_list = result
        else :
            print(help_str)
            sys.exit(1)

    cur_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    log_file = "log/auto-hunter-trade-done-%s.txt"%cur_time
    f_trade_done = open(log_file, mode='w')
    #print("tail -f "+log_file)


    threading.Thread(target=loop_handle).start()
    time.sleep(2)
    threading.Thread(target=myEventHandle).start()




