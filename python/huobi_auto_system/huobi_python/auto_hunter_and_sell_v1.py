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
import inspect

#can be updated by config_symbol(sym) default value is for eth3
symbol = "eth3lusdt"
balance_name = "eth3l"
price_precision = 10000 #price 价格精度
price_print_format= 4  #%.4f  --> %.*f %(4)
amount_precision = 10000  #交易数量精度
db_program_id = 2  #eth3
big_change_threhold = 1  # 1% in 12 seconds
diff_space_buy = 2.5   #1.2% 和上一个买入价格的距离需要达到这个值，以防买入太密集（下跌时候的指标）-b
diff_space_sell = 2 #1%  超过10次上涨后，达到这个涨价幅度则卖出 -s
deal_space = 2.5  #1.667% 上涨后，达到这个涨价幅度则卖出 -d
accu_buy = 0.6 #0.6% 超过10次后，累计的下跌幅度达到这个值，才可以买入，以防超过10次下跌，但实际下跌幅度很小的可能 -a


loop_time = 3  #seconds
ORDER_TIMEOUT_LOOP_TIMES = int(5*60/loop_time)  #5 minutes 如果订单提交后5分钟没成交，则取消订单
JUST_BUY_TIME = int(6*60/loop_time)  #6 minutes 购买6分钟内，不会再次触发购买
BIG_DROP_TIME = int(5*60/loop_time)  #5 minutes 大跌后，这个标志存在5分钟，以给最后last_several_times_restrict次购买提供参考
buy_space_times_if_cannot_meet_accu_buy = 3 # if cann't meet accu buy, but price space meet 3 times buy_price > current_price + 3*diff_space_buy_val
buy_space_times_if_cannot_meet_big_drop = 2.5
trade_fee_deduct_from_symbol = True  #交易费用是从当前买入的symbol里扣除的，这样卖的时候需要考虑买入扣除交易费用部分，另一种是积分扣除
trade_fee_deduct_value = 0.002 #huobi是千分之2的交易费用
price_q_eq_size = 5
minute_price_q_size = 30
last_several_times_restrict = 2

state_buying = 1
state_partial_bought = 2
state_bought = 3
state_selling = 4
state_partial_selled = 5
state_selled = 6

inc_order_flag = 1
dec_order_flag = 2

buy_order_ongoing = False
sell_order_ongoing = False

lock = threading.Lock()

db = MySQLdb.connect("localhost", "root", "abcd.12345", "ecoin_system", charset='gb2312' )
cursor = db.cursor()

def config_symbol(sym):
    global symbol
    global balance_name
    global price_precision
    global price_print_format
    global amount_precision
    global db_program_id
    global big_change_threhold
    global diff_space_buy
    global diff_space_sell
    global deal_space
    global accu_buy

    if sym=="eth3l":
        symbol = "eth3lusdt"
        balance_name = "eth3l"
        price_precision = 10000 #price 价格精度
        price_print_format= 4  #%.4f  --> %.*f %(4)
        amount_precision = 10000  #交易数量精度
        db_program_id = 2  #eth3
        big_change_threhold = 1

        diff_space_buy = 2.5   #% 和上一个买入价格的距离需要达到这个值，以防买入太密集（下跌时候的指标）
        diff_space_sell = 2 #% 超过10次上涨后，达到这个涨价幅度则卖出
        deal_space = 2.5  #% 上涨后，达到这个涨价幅度则卖出
        accu_buy = 0.6 #% 超过10次后，累计的下跌幅度达到这个值，才可以买入，以防超过10次下跌，但实际下跌幅度很小的可能

        print("config eth3l hunter.")
    elif sym=="eth":
        symbol = "ethusdt"
        balance_name = "eth"
        price_precision = 100 #price 价格精度
        price_print_format= 2  #%.4f  --> %.*f %(4)
        amount_precision = 10000  #交易数量精度
        db_program_id = 1  #eth
        big_change_threhold = 0.6  # 0.6% in 12 seconds

        diff_space_buy = 3   #% 和上一个买入价格的距离需要达到这个值，以防买入太密集（下跌时候的指标）
        diff_space_sell = 1.667 #%  超过10次上涨后，达到这个涨价幅度则卖出
        deal_space = 2  #% 上涨后，达到这个涨价幅度则卖出
        accu_buy = 0.5 #% 超过10次后，累计的下跌幅度达到这个值，才可以买入，以防超过10次下跌，但实际下跌幅度很小的可能
        print("config eth hunter.")
    elif sym=="eth3s":
        symbol = "eth3susdt"
        balance_name = "eth3s"
        price_precision = 100000000 #price 价格精度
        price_print_format= 8  #%.4f  --> %.*f %(4)
        amount_precision = 10000  #交易数量精度
        db_program_id = 3  #eth
        big_change_threhold = 1  # 0.6% in 12 seconds

        diff_space_buy = 4   #和上一个买入价格的距离要达到这个值，以防买入太密集（下跌时候的指标）
        diff_space_sell = 2 #%  超过10次上涨后，达到这个涨价幅度则卖出
        deal_space = 3  #% 上涨后，达到这个涨价幅度则卖出
        accu_buy = 0.8 #% 超过10次后，累计的下跌幅度达到这个值，才可以买入，以防超过10次下跌，但实际下跌幅度很小的可能
        print("config eth3s hunter.")
    else:
        print("config eth3 as default.")

#buy=1, sell=2
def check_order_in_db(symbol, buy_sell, price, db_program_id):
    cursor = db.cursor()
    #print(symbol, buy_sell, price)
    sql = "SELECT * FROM deal_table \
       WHERE symbol='%s' and buy_sell=%d and program=%d" % (symbol, buy_sell, db_program_id)
    #print(sql)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            id = row[0]
            orderid = row[1]
            symbol = row[2]
            buy_sell = row[3]
            db_price = row[4]
            #amount = row[4]
            #print("id=%s, orderid=%s, symbol=%s, buy_sell=%s, price=%s, amount=%s" % \
            #        (id, orderid, symbol, buy_sell, price, amount))
            if price == db_price:
                return orderid
            else:
                send_email("HB: " + "check_order_in_db error ", "price %.*f is different with db_price %.*f"% (price_print_format, price, price_print_format, db_price))

        return 0
    except:
        #print("Error: unable to fecth data")
        return 0

def get_deal_state(order_id, is_buy_orderid):
    cursor = db.cursor()
    if is_buy_orderid:
        orderid_type = "buy_orderid"
    else:
        orderid_type = "sell_orderid"

    sql = "SELECT state FROM deal_table \
       WHERE %s=%d" % (orderid_type, order_id)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            state = row[0]
        return state
    except:
        print("Error: get_deal_state")
        return 0

def buy_insert_into_db(order_id, symbol, state_buying, buy_price, amount)
    cursor = db.cursor()
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    sql = "INSERT INTO deal_table(buy_orderid, \
            symbol, state, buy_price, amount, create_time) \
            VALUES (%d, '%s', %d, %.*f, %f, '%s')"% (orderid, symbol, state_buying, price_print_format, buy_price, amount, cur_time)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def buy_update_db(order_id, state)
    cursor = db.cursor()
    state_db = get_deal_state(order_id, True)
    if state_db == 0:
        print("ERROR to get state from db")
    if state < state_db:
        print("ERROR: sth wrong db state=%d, new state=%d"%(state_db, state))

    sql = "update deal_table set state=%d where buy_orderid=%d"%(state, orderid)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def remove_order_in_db(orderid):
    return #no removed needed here
    sql = "delete from deal_table where orderid=%d"%(orderid)
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
        printme("created BUY order id : %d price=%.*f, amount=%f\n"%(order_id, price_print_format, price, amount))
        return True, order_id, 0
    except Exception as e:
        print("ExecuteError:", e, inspect.stack()[1][4])
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
        print("ExecuteError:", e, inspect.stack()[1][4])
        return False, 0

def get_current_price(symbol):
    try:
        market_client = MarketClient()
        depth_size = 2
        depth = market_client.get_pricedepth(symbol, DepthStep.STEP0, depth_size)
        #LogInfo.output("---- Top {size} bids ----".format(size=len(depth.bids)))
        i = 0
        if not depth:
            return 0

        for entry in depth.bids:
            i = i + 1
            if i == 1:
                first_price = entry.price
                return first_price
            #LogInfo.output(str(i) + ": price: " + str(entry.price) + ", amount: " + str(entry.amount))
    except Exception as e:
        print("ExecuteError in get_current_price", e)
        return 0

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

def get_first_value(list_value):
    if len(list_value):
        ret = list_value[0].strip()
    else:
        ret=""
    return ret

def translate_state(order_type, order_state):
    if order_type=="sell-limit" and order_state = "partial-filled":
        return  state_partial_selled
    elif order_type=="sell-limit" and order_state = "filled":
        return state_selled
    elif order_type=="buy-limit" and order_state = "filled":
        return state_bought
    elif order_type=="buy-limit" and order_state = "partial-filled":
        return state_partial_bought
    else:
        print(ERROR)

def handle_order_id(order_id, order_type, price, order_state):
    lock.acquire()
    global buy_order_ongoing
    global sell_order_ongoing
    global price_list
    global f_trade_done
    global just_buy_time_out # 6 minutes
    global symbol
    global usdt_amount
    global trade_fee_deduct_value
    global trade_fee_deduct_from_symbol

    print("start to handle order id %d now"%order_id)
    if order_type=="sell-limit":
        buy_update_db(order_id, translate_state(order_type, order_state))
        if order_state = "partial-filled":
            return
        buy_price  = get_previous_price(price_list)
        if len(price_list):
            price_list.pop()
        #remove_order_in_db(order_id)

        if trade_fee_deduct_from_symbol:
            total_num = int((usdt_amount*(1-trade_fee_deduct_value)/buy_price)*amount_precision)/amount_precision
        else:
            total_num = int((usdt_amount/buy_price)*amount_precision)/amount_precision

        output_to_log_file(f_trade_done, "%s SELL done: %.*f buy:%.*f diff:%.*f amount=%.*f\n"%(symbol, price_print_format, price, price_print_format, buy_price, price_print_format, price-buy_price, price_print_format, total_num))
        sell_order_ongoing = False
        just_buy_time_out = 0
        buy_update_db(order_id, order_state)
    elif order_type=="buy-limit":
        remove_order_in_db(order_id)
        price_list.append(price)
        output_to_log_file(f_trade_done, "%s BUY done: %.*f amount=%.*f %r \n"%(symbol, price_print_format, price, price_print_format, usdt_amount/price, price_list))
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

        o_state = get_first_value(order_state)
        if  o_state != "partial-filled" and o_state != "filled":
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

        handle_order_id(order_id, order_type, price, order_state)

    except Exception as e:
        print("ExecuteError in handle_order_update", e, inspect.stack()[1][4])

def cancel_order_and_restore_system(symbol, orderid):
    order_list = []
    order_list.append(orderid)
    batch_cancel_orders(symbol, order_list)
    remove_order_in_db(orderid)

def sell_policy_analyse(f_trade_done, which_queue, inc_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val,diff_space_buy,usdt_amount,accu_buy_val, accu_buy, price_list):
    output_to_log_file(f_trade_done, "sell %.*f %s analyse: ===================start=================="%(price_print_format, current_price, which_queue), True)
    output_to_log_file(f_trade_done, "sell %.*f %s analyse: times:%d/%d diff:%.*f"%(price_print_format, current_price, which_queue, already_buy_times, total_buy_times, price_print_format, current_price-buy_price))
    output_to_log_file(f_trade_done,"Q --%d/++%d %s %r"%(q_accu_dec, q_accu_inc, qstr, q.queue))
    output_to_log_file(f_trade_done,"EQ --%d/++%d %s %r"%(eq_accu_dec, eq_accu_inc, eqstr, eq.queue))
    if big_drop_flag:
        output_to_log_file(f_trade_done,"BIGDROP:%d %sgap:%s sell/deal=%.*f(%.3f%%)/%.*f(%.3f%%) buy_space=%.*f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_drop_flag_time_out, big_change_str, showgap, price_print_format, diff_space_sell_val, diff_space_sell, price_print_format, deal_space_val, deal_space, price_print_format, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))
    else:
        output_to_log_file(f_trade_done,"%sgap:%s sell/deal=%.*f(%.3f%%)/%.*f(%.3f%%) buy_space=%.*f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_change_str, showgap, price_print_format, diff_space_sell_val, diff_space_sell, price_print_format, deal_space_val, deal_space, price_print_format, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))

    output_to_log_file(f_trade_done,"inc:%.*f accu_buy:%.*f/%.3f%% price list: %r"%(price_print_format, current_price-inc_start, price_print_format, accu_buy_val, accu_buy, price_list))
    output_to_log_file(f_trade_done, "sell %.*f %s analyse: ===================end==================="%(price_print_format, current_price, which_queue))

def buy_policy_analyse(f_trade_done, which_queue, dec_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq, big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list):
    output_to_log_file(f_trade_done, "buy %.*f %s analyse: ===================start=================="%(price_print_format, current_price, which_queue), True)
    output_to_log_file(f_trade_done, "buy %.*f %s analyse: times:%d/%d diff:%.*f"%(price_print_format,current_price, which_queue, already_buy_times, total_buy_times, price_print_format, buy_price - current_price))
    output_to_log_file(f_trade_done,"Q --%d/++%d %s %r"%(q_accu_dec, q_accu_inc, qstr, q.queue))
    output_to_log_file(f_trade_done,"EQ --%d/++%d %s %r"%(eq_accu_dec, eq_accu_inc, eqstr, eq.queue))
    if big_drop_flag:
        output_to_log_file(f_trade_done,"BIGDROP:%d %sgap:%s sell/deal=%.*f(%.3f%%)/%.*f(%.3f%%) buy_space=%.*f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_drop_flag_time_out, big_change_str, showgap, price_print_format, diff_space_sell_val, diff_space_sell, price_print_format, deal_space_val, deal_space, price_print_format, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))
    else:
        output_to_log_file(f_trade_done,"%sgap:%s sell/deal=%.*f(%.3f%%)/%.*f(%.3f%%) buy_space=%.*f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_change_str, showgap, price_print_format, diff_space_sell_val, diff_space_sell, price_print_format, deal_space_val, deal_space, price_print_format, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))

    output_to_log_file(f_trade_done,"dec:%.*f accu_buy:%.*f/%.3f%% price list: %r"%(price_print_format, dec_start-current_price, price_print_format, accu_buy_val, accu_buy, price_list))
    output_to_log_file(f_trade_done, "buy %.*f %s analyse: ===================end==================="%(price_print_format,current_price, which_queue))

def cal_minute_change_percent(minute_price_q):
    cur_qsize = minute_price_q.qsize()
    result_str = ""
    if cur_qsize>= 5:
        five_percent = (minute_price_q.queue[cur_qsize-1]-minute_price_q.queue[cur_qsize-5])*100/minute_price_q.queue[cur_qsize-5]
        result_str = "5:%.2f%%"%(five_percent)
    else:
        five_percent = 0

    if cur_qsize>= 15:
        fifteen_percent = (minute_price_q.queue[cur_qsize-1]-minute_price_q.queue[cur_qsize-15])*100/minute_price_q.queue[cur_qsize-15]
        result_str += " 15:%.2f%%"%(fifteen_percent)
    else:
        fifteen_percent = 0

    if cur_qsize>= 30:
        thirty_percent = (minute_price_q.queue[cur_qsize-1]-minute_price_q.queue[cur_qsize-30])*100/minute_price_q.queue[cur_qsize-30]
        result_str += " 30:%.2f%%"%(thirty_percent)
    else:
        thirty_percent = 0

    return result_str, five_percent, fifteen_percent, thirty_percent

def loop_handle():
    q = queue.Queue()
    eq = queue.Queue()
    minute_price_q = queue.Queue()


    steps_dec = 10
    q_accu_dec = 0
    eq_accu_dec = 0

    steps_inc = 10
    q_accu_inc = 0
    eq_accu_inc = 0

    current_price = get_current_price(symbol)
    q_accu_inc_start = current_price
    q_accu_dec_start = current_price
    eq_accu_inc_start = current_price
    eq_accu_dec_start = current_price

    buying = 0
    selling = 0
    order_timeout_checking = 0
    big_drop_flag = False
    big_drop_flag_time_out = 0
    minute_control = 0
    minute_percent = ""

    global big_change_threhold
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

    cur_time = time.strftime("%Y-%m-%d", time.localtime())
    log_file = "log/auto-hunter-price-big-change-%s-%s.txt"%(balance_name,cur_time)
    f_price_big_change = open(log_file, mode='a')

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

        put_into_queue(q, current_price, price_q_eq_size)
        q_order, q_even, q_diff = order_even_value(q)

        if minute_control == 0:
            put_into_queue(minute_price_q, q_even, minute_price_q_size)
            minute_control += 1
        elif minute_control >= 20:
            minute_control = 0
        else:
            minute_control += 1

        put_into_queue(eq, q_even, price_q_eq_size)
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
            output_to_log_file(f_price_big_change, "Q-UPUPUP: %.2f%%, q_even:%.*f, q_diff=%.*f"%(q_diff_percent, price_print_format, q_even, price_print_format,q_diff))
            big_drop_flag = False
        elif q_diff_percent < -big_change_threhold:
            big_change_str = "Q-DOWNDOWN %.2f%% "%(q_diff_percent)
            big_drop_flag = True
            big_drop_flag_time_out = BIG_DROP_TIME
            output_to_log_file(f_price_big_change, "Q-DOWNDOWN: %.2f%%, q_even:%.*f, q_diff=%.*f"%(q_diff_percent, price_print_format, q_even, price_print_format,q_diff))

        if eq_diff_percent > big_change_threhold:
            big_change_str += "EQ-UPUPUP %.2f%% "%(eq_diff_percent)
            output_to_log_file(f_price_big_change, "EQ-UPUPUP: %.2f%%, eq_even:%.*f, eq_diff=%.*f"%(eq_diff_percent, price_print_format,eq_even, price_print_format,eq_diff))
            big_drop_flag = False
        elif eq_diff_percent < -big_change_threhold:
            big_change_str += "EQ-DOWNDOWN %.2f%% "%(eq_diff_percent)
            big_drop_flag = True
            big_drop_flag_time_out = BIG_DROP_TIME
            output_to_log_file(f_price_big_change, "EQ-DOWNDOWN: %.2f%%, eq_even:%.*f, eq_diff=%.*f"%(eq_diff_percent, price_print_format, eq_even, price_print_format, eq_diff))

        if buy_order_ongoing:
            #orderid = check_order_in_db(symbol, , buying, db_program_id)
            if not orderid:
                printme_warning("buy %.*f is not found in local DB!!!"% (price_print_format, buying))
                send_email("HB: " + "buy_order_ongoing error ", "buy %.*f is not found in local DB!!!"% (price_print_format, buying))
                #buy_order_ongoing = False #好像有问题，这里会导致再次购买，所以把这个注释掉先
            
            if order_timeout_checking > 1 :
                order_timeout_checking -=  1
            else:
                order_timeout_checking = 0
                printme("canceling buy order id %d"%orderid)
                cancel_order_and_restore_system(symbol, orderid)
                buy_order_ongoing = False
                buying = 0

        if sell_order_ongoing:
            orderid = check_order_in_db(symbol, sell_db_flag, selling, db_program_id)
            if not orderid:
                printme_warning("sell %.*f is not found in local DB!!!"% (price_print_format, selling))
                send_email("HB: " + "sell_order_ongoing error ", "sell %.*f is not found in local DB!!!"% (price_print_format, selling))
                #sell_order_ongoing = False

            if order_timeout_checking > 1 :
                order_timeout_checking -= 1
            else:
                order_timeout_checking = 0
                printme("canceling sell order id %d"%orderid)
                cancel_order_and_restore_system(symbol, orderid)
                sell_order_ongoing = False
                selling = 0

        if q_order == inc_order_flag:
            q_accu_inc += 1
            if q_accu_inc == 1:
                q_accu_inc_start = get_last_second_value(q)
            elif q_accu_inc == 0:
                q_accu_inc_start = current_price
            qstr = "Q is ++ adiff:%.*f Qdiff:%.*f %.2f%%"%(price_print_format, current_price-q_accu_inc_start, price_print_format, q_diff, q_diff_percent)

            if just_buy_time_out == 0 and (q_accu_dec_start-current_price > accu_buy_val or buy_price > current_price + buy_space_times_if_cannot_meet_accu_buy*diff_space_buy_val) and already_buy_times < total_buy_times and not buy_order_ongoing and q_accu_dec >= steps_dec and (buy_price > current_price + diff_space_buy_val or buy_price==0):
                if (already_buy_times + last_several_times_restrict >= total_buy_times and (big_drop_flag or buy_price > current_price + buy_space_times_if_cannot_meet_big_drop*diff_space_buy_val)) or already_buy_times + last_several_times_restrict < total_buy_times:
                    ret = handle_buy_order(symbol, current_price, usdt_amount)
                    if ret:
                        buy_order_ongoing = True
                        buying = current_price
                        order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                        buy_policy_analyse(f_trade_done, "Q", q_accu_dec_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)
                elif already_buy_times + last_several_times_restrict >= total_buy_times and not big_drop_flag:
                    output_to_log_file(f_trade_done, "CANCEL Q buy for last times %d/%d, no big drop. cur_price:%.*f diff:%.*f"%(already_buy_times, total_buy_times, price_print_format, current_price, price_print_format, buy_price - current_price))


            if q_accu_inc >= 2:
                q_accu_dec = 0

        elif q_order == dec_order_flag:
            q_accu_dec += 1
            if q_accu_dec == 1:
                q_accu_dec_start = get_last_second_value(q)
            elif q_accu_dec == 0:
                q_accu_dec_start = current_price
            qstr = "Q is -- adiff:%.*f Qdiff:%.*f %.2f%%"%(price_print_format,current_price-q_accu_dec_start, price_print_format,q_diff, q_diff_percent)

            if not sell_order_ongoing and current_price-buy_price > diff_space_sell_val and buy_price:
                ret = handle_sell_order(symbol, current_price, usdt_amount, buy_price)
                if ret:
                    sell_order_ongoing = True
                    selling = current_price
                    order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                    sell_policy_analyse(f_trade_done, "Q", q_accu_inc_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)
            if q_accu_dec >= 2:
                q_accu_inc = 0
        else:
            qstr = "        Qdiff:%.*f %.2f%%"%(price_print_format,q_diff, q_diff_percent)
            if not sell_order_ongoing and current_price - buy_price > deal_space_val and buy_price:
                ret = handle_sell_order(symbol, current_price, usdt_amount, buy_price)
                if ret:
                    sell_order_ongoing = True
                    selling = current_price
                    order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                    if eq_accu_inc_start < q_accu_inc_start:
                        inc_start = eq_accu_inc_start
                        which_queue = "EQ"
                    else:
                        inc_start = q_accu_inc_start
                        which_queue = "Q"
                    sell_policy_analyse(f_trade_done, which_queue, inc_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)

        if eq_order == inc_order_flag:
            eq_accu_inc += 1
            if eq_accu_inc == 1:
                eq_accu_inc_start = get_last_second_value(q)
            elif eq_accu_inc == 0:
                eq_accu_inc_start = current_price

            eqstr = "EQ is ++ adiff:%.*f EQdiff:%.*f %.2f%%" %(price_print_format, current_price-eq_accu_inc_start, price_print_format, eq_diff, eq_diff_percent)

            if just_buy_time_out == 0 and (eq_accu_dec_start-current_price > accu_buy_val or buy_price > current_price + buy_space_times_if_cannot_meet_accu_buy*diff_space_buy_val) and already_buy_times < total_buy_times and not buy_order_ongoing and eq_accu_dec >= steps_dec and (buy_price > current_price + diff_space_buy_val or buy_price==0):
                if (already_buy_times + last_several_times_restrict >= total_buy_times and (big_drop_flag or buy_price > current_price + buy_space_times_if_cannot_meet_big_drop*diff_space_buy_val)) or already_buy_times + last_several_times_restrict < total_buy_times:
                    ret = handle_buy_order(symbol, current_price, usdt_amount)
                    if ret:
                        buy_order_ongoing = True
                        buying = current_price
                        order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                        buy_policy_analyse(f_trade_done, "EQ", eq_accu_dec_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)
                elif already_buy_times + last_several_times_restrict >= total_buy_times and not big_drop_flag:
                    output_to_log_file(f_trade_done, "CANCEL EQ buy for last times %d/%d, no big drop. cur_price:%.*f diff:%.*f"%(already_buy_times, total_buy_times, price_print_format, current_price, price_print_format, buy_price - current_price))


            if eq_accu_inc >= 2:
                eq_accu_dec = 0

        elif eq_order == dec_order_flag:
            eq_accu_dec += 1
            if eq_accu_dec == 1:
                eq_accu_dec_start = get_last_second_value(q)
            elif eq_accu_dec == 0:
                eq_accu_dec_start = current_price
            eqstr = "EQ is -- adiff:%.*f EQdiff:%.*f %.2f%%"%(price_print_format, current_price-eq_accu_dec_start, price_print_format, eq_diff, eq_diff_percent)

            if not sell_order_ongoing and (current_price-buy_price) > diff_space_sell_val and buy_price:
                ret = handle_sell_order(symbol, current_price, usdt_amount, buy_price)
                if ret:
                    sell_order_ongoing = True
                    selling = current_price
                    order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                    sell_policy_analyse(f_trade_done, "EQ", eq_accu_inc_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)

            if eq_accu_dec >= 2:
                eq_accu_inc = 0
        else:
            eqstr = "         EQdiff:%.*f %.2f%%"%(price_print_format, eq_diff, eq_diff_percent)
            if not sell_order_ongoing and current_price-buy_price > deal_space_val and buy_price:
                ret = handle_sell_order(symbol, current_price, usdt_amount, buy_price)
                if ret:
                    sell_order_ongoing = True
                    selling = current_price
                    order_timeout_checking = ORDER_TIMEOUT_LOOP_TIMES
                    if eq_accu_inc_start < q_accu_inc_start:
                        inc_start = eq_accu_inc_start
                        which_queue = "EQ"
                    else:
                        inc_start = q_accu_inc_start
                        which_queue = "Q"
                    sell_policy_analyse(f_trade_done, which_queue, inc_start, big_drop_flag, current_price, already_buy_times, total_buy_times, buy_price, q_accu_dec, q_accu_inc, qstr, q, eq_accu_dec, eq_accu_inc, eqstr, eq,big_drop_flag_time_out, big_change_str, showgap, diff_space_sell_val, diff_space_sell, deal_space_val, deal_space, diff_space_buy_val, diff_space_buy, usdt_amount,accu_buy_val, accu_buy, price_list)

        showgap = ""
        if buy_price:
            showgap = "%.*f"%(price_print_format, current_price-buy_price)

        if buy_order_ongoing:
            printme("buying %.*f"%(price_print_format,buying))
        if sell_order_ongoing:
            printme("selling %.*f"%(price_print_format,selling))
        if qstr or eqstr:
            printme("--%d/++%d %s %r"%(q_accu_dec, q_accu_inc, qstr, q.queue))
            printme("--%d/++%d %s %r"%(eq_accu_dec, eq_accu_inc, eqstr, eq.queue))
        else:
            printme("cur_price=%.*f"%(price_print_format, current_price))
        
        if big_drop_flag:
            printme("BIGDROP:%d %sgap:%s sell/deal=%.*f(%.3f%%)/%.*f(%.3f%%) buy_space=%.*f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_drop_flag_time_out, big_change_str, showgap, price_print_format,diff_space_sell_val, diff_space_sell, price_print_format, deal_space_val, deal_space, price_print_format, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))
        else:
            printme("%sgap:%s sell/deal=%.*f(%.3f%%)/%.*f(%.3f%%) buy_space=%.*f(%.3f%%) usdt:%d buy_times=%d/%d"%(big_change_str, showgap, price_print_format, diff_space_sell_val, diff_space_sell, price_print_format, deal_space_val, deal_space, price_print_format, diff_space_buy_val, diff_space_buy, usdt_amount,already_buy_times, total_buy_times))

        printme("cur_price=%.*f buy_timeout:%d accu_buy:%.*f/%.2f%% price list: %r"%(price_print_format, current_price, just_buy_time_out, price_print_format, accu_buy_val, accu_buy, price_list))

        if minute_control == 1:
            minute_percent, five_percent, fifteen_percent, thirty_percent = cal_minute_change_percent(minute_price_q)
        
        printme("last_times:%d %s"%(last_several_times_restrict, minute_percent))
        #if qstr or eqstr:
        printme("==================================================================================================================\n")
        lock.release()
        time.sleep(loop_time)

def error_handler(exception: 'HuobiApiException'):
    send_email("HB: " + "subscribe error happened", exception)


def myEventHandle():
        #trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key, init_log=True)
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key, init_log=False)
        trade_client.sub_order_update(symbol, handle_order_update)

def put_into_queue(q, value, q_size):
    if q.qsize() >= q_size:
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

    e_value = int(total *price_precision / q.qsize())/price_precision
    if inc_flag:
        order = inc_order_flag
        #diff = last_item - first_item
    elif dec_flag:
        order = dec_order_flag
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

def handle_buy_order(symbol, buy_price, usdt_amount):
    buy_price = int( buy_price*price_precision)/price_precision
    usdt_bal = float(get_trade_balance("usdt"))
    buy_amount = usdt_amount
    if usdt_amount > usdt_bal and usdt_bal < 50:
        printme_warning("usdt balance is %f, less than required value %f !"% (usdt_bal, usdt_amount))
        return False
    elif usdt_amount > usdt_bal and usdt_bal > 50:
        buy_amount = usdt_bal

    total_num = int((buy_amount/ buy_price )*amount_precision)/amount_precision
    ret, order_id, max_size = create_buy_order(symbol, buy_price, total_num)
    if ret:
        ret = buy_insert_into_db(order_id, symbol, state_buying, buy_price, total_num)
        printme_warning("creatd order id %s in local db!"% (order_id))
    return ret

def handle_sell_order(symbol, sell_price, usdt_amount, buy_price):
    global trade_fee_deduct_value
    global trade_fee_deduct_from_symbol

    sell_price = int(sell_price*price_precision)/price_precision
    buy_price = int(buy_price*price_precision)/price_precision
    if trade_fee_deduct_from_symbol:
        total_num = int((usdt_amount*(1-trade_fee_deduct_value)/buy_price)*amount_precision)/amount_precision
    else:
        total_num = int((usdt_amount/buy_price)*amount_precision)/amount_precision
    account_bal = float(get_trade_balance(balance_name))
    account_bal = int(account_bal*amount_precision)/amount_precision

    if account_bal < total_num:
        total_num = account_bal
    
    ret, order_id = create_sell_order(symbol, sell_price, total_num)

    if ret:
        selling_update_deal_db(order_id, symbol, sell_db_flag, sell_price, total_num, db_program_id)
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
    total_buy_times = 10
    just_buy_time_out = 0

    help_str = "auto_hunter_v2.py -b <diff_space_buy %> -a <accu_buy % > -s <diff_space_sell % > -l <last_times> -d <deal_space % > -u <usdt_amount> -y <symbol> -p <price_list> -t <total_buy_times>"

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hb:s:d:u:p:t:a:y:l:",["help", "diff_space_buy=","last_times=","accu_buy=","diff_space_sell=","deal_space=","usdt_amount=","symbol=","price_list=","total_buy_times="])
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
        elif opt in ("-l", "--last_times"):
            last_several_times_restrict = int(arg)
        elif opt in ("-y", "--symbol"):
            config_symbol(arg)
            symbol_configed = True
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

    cur_time = time.strftime("%Y-%m-%d", time.localtime())
    log_file = "log/auto-hunter-trade-done-%s-%s.txt"%(balance_name,cur_time)
    f_trade_done = open(log_file, mode='a')
    #print("tail -f "+log_file)


    threading.Thread(target=loop_handle).start()
    time.sleep(2)
    threading.Thread(target=myEventHandle).start()




