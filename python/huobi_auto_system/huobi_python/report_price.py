#!/usr/bin/python3

from huobi.client.trade import TradeClient
from huobi.constant import *
from huobi.utils import *
from autonomy import __Autonomy__
import re, os
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

from configparser import ConfigParser

ini_file = "hunter.ini"
db_name = "mysql"
cfg = ConfigParser()
cfg.read(ini_file)

db_cfg = dict(cfg.items(db_name))
db = MySQLdb.connect(db_cfg['host'], db_cfg['user'], db_cfg['password'], db_cfg['database'], charset='gb2312' )
cursor = db.cursor()


general_cfg = dict(cfg.items('general'))
loop_time = int(general_cfg['loop_time'])  #seconds
ORDER_TIMEOUT_LOOP_TIMES = int(int(general_cfg['order_timeout'])*60/loop_time) #5 minutes 如果订单提交后5分钟没成交，则取消订单
JUST_BUY_TIME = int(int(general_cfg['just_buy_time'])*60/loop_time)  #6 minutes 购买6分钟内，不会再次触发购买
BIG_DROP_TIME = int(int(general_cfg['big_drop_time'])*60/loop_time)  #5 minutes 大跌后，这个标志存在5分钟，以给最后last_several_times_restrict次购买提供参考
buy_space_times_if_cannot_meet_accu_buy = float(general_cfg['buy_space_times_if_cannot_meet_accu_buy']) # if cann't meet accu buy, but price space meet 3 times buy_price > current_price + 3*diff_space_buy_val
buy_space_times_if_cannot_meet_big_drop = float(general_cfg['buy_space_times_if_cannot_meet_big_drop'])
trade_fee_deduct_from_symbol = general_cfg['trade_fee_deduct_from_symbol']  #交易费用是从当前买入的symbol里扣除的，这样卖的时候需要考虑买入扣除交易费用部分，另一种是积分扣除
trade_fee_deduct_value = float(general_cfg['trade_fee_deduct_value']) #huobi是千分之2的交易费用
last_several_times_restrict = int(general_cfg['last_several_times_restrict'])
steps_dec = int(general_cfg['steps_dec'])
first_buy_price_threshold = float(general_cfg['first_buy_price_threshold'])
quick_sell_flag = general_cfg['quick_sell_flag']
account_id = int(general_cfg['account_id'])
g_api_key = general_cfg['g_api_key']
g_secret_key = general_cfg['g_secret_key']

#print(trade_fee_deduct_from_symbol)
db_enabled = general_cfg['db_enabled']

default_symbol = general_cfg['default_symbol']
symbol_cfg = dict(cfg.items(default_symbol))

#can be updated by config_symbol(sym) default value is for eth3
symbol = symbol_cfg['symbol']
balance_name = symbol_cfg['balance_name']
price_precision = int(symbol_cfg['price_precision']) #price 价格精度
price_print_format= int(symbol_cfg['price_print_format'])  #%.4f  --> %.*f %(4)
amount_precision = int(symbol_cfg['amount_precision'])  #交易数量精度
db_program_id = int(symbol_cfg['db_program_id'])  #eth3
big_change_threhold = float(symbol_cfg['big_change_threhold'])  # 1% in 12 seconds
diff_space_buy = float(symbol_cfg['diff_space_buy'])   #1.2% 和上一个买入价格的距离需要达到这个值，以防买入太密集（下跌时候的指标）-b
diff_space_sell = float(symbol_cfg['diff_space_sell']) #1%  超过10次上涨后，达到这个涨价幅度则卖出 -s
deal_space = float(symbol_cfg['deal_space'])  #1.667% 上涨后，达到这个涨价幅度则卖出 -d
accu_buy = float(symbol_cfg['accu_buy']) #0.6% 超过10次后，累计的下跌幅度达到这个值，才可以买入，以防超过10次下跌，但实际下跌幅度很小的可能 -a



not_found_in_local_DB_send_email = False
price_q_eq_size = 5
minute_price_q_size = 30

inc_order_flag = 1
dec_order_flag = 2

buy_db_flag = 1 #buy=1, sell=2
sell_db_flag = 2

buy_order_ongoing = False
sell_order_ongoing = False
partial_filled_flag = False

lock = threading.Lock()



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

    symbol_cfg = dict(cfg.items(sym))
    #can be updated by config_symbol(sym) default value is for eth3
    symbol = symbol_cfg['symbol']
    balance_name = symbol_cfg['balance_name']
    price_precision = int(symbol_cfg['price_precision']) #price 价格精度
    price_print_format= int(symbol_cfg['price_print_format'])  #%.4f  --> %.*f %(4)
    amount_precision = int(symbol_cfg['amount_precision'])  #交易数量精度
    db_program_id = int(symbol_cfg['db_program_id'])  #eth3
    big_change_threhold = float(symbol_cfg['big_change_threhold'])  # 1% in 12 seconds
    diff_space_buy = float(symbol_cfg['diff_space_buy'])   #1.2% 和上一个买入价格的距离需要达到这个值，以防买入太密集（下跌时候的指标）-b
    diff_space_sell = float(symbol_cfg['diff_space_sell']) #1%  超过10次上涨后，达到这个涨价幅度则卖出 -s
    deal_space = float(symbol_cfg['deal_space'])  #1.667% 上涨后，达到这个涨价幅度则卖出 -d
    accu_buy = float(symbol_cfg['accu_buy']) #0.6% 超过10次后，累计的下跌幅度达到这个值，才可以买入，以防超过10次下跌，但实际下跌幅度很小的可能 -a

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

def insert_into_db(orderid, symbol, buy_sell, price, amount, db_program_id):
    cursor = db.cursor()
    sql = "INSERT INTO trade_order(orderid, \
            symbol, buy_sell, price, amount, program) \
            VALUES (%d, '%s', %d, %.*f, %f, %d)"% (orderid, symbol, buy_sell, price_print_format, price, amount, db_program_id)
    try:
        cursor.execute(sql)
        db.commit()
        print(sql)
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
            i += 1
            if i == 1:
                first_price = entry.price
                return first_price
            #LogInfo.output(str(i) + ": price: " + str(entry.price) + ", amount: " + str(entry.amount))
    except Exception as e:
        print("ExecuteError in get_current_price", e)
        send_email("HB: " + "get_current_price Exception ", "you can have a check if it is break or not after using pass!")
        pass
    return 0

def get_trade_balance(bal_name):
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

def handle_order_id(order_id, order_type, price):
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
        buy_price  = get_previous_price(price_list)
        if len(price_list):
            price_list.pop()
        if db_enabled:
            remove_order_in_db(order_id)

        if trade_fee_deduct_from_symbol:
            total_num = int((usdt_amount*(1-trade_fee_deduct_value)/buy_price)*amount_precision)/amount_precision
        else:
            total_num = int((usdt_amount/buy_price)*amount_precision)/amount_precision

        output_to_log_file(f_trade_done, "%s SELL done: %.*f buy:%.*f diff:%.*f amount=%.*f income=%.1f\n"%(symbol, price_print_format, price, price_print_format, buy_price, price_print_format, price-buy_price, price_print_format, total_num, total_num*(price-buy_price)*6.4*0.998))
        sell_order_ongoing = False
        just_buy_time_out = 0
    elif order_type=="buy-limit":
        if db_enabled:
            remove_order_in_db(order_id)
        price_list.append(price)
        output_to_log_file(f_trade_done, "%s BUY done: %.*f amount=%.*f %r \n"%(symbol, price_print_format, price, price_print_format, usdt_amount/price, price_list))
        buy_order_ongoing = False
        just_buy_time_out = JUST_BUY_TIME

    else:
        print("sth wrong? order_type=%s"%order_type)
    lock.release()

def handle_order_update(upd_event: 'OrderUpdateEvent'):
    global partial_filled_flag

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
        if  o_state == "partial-filled":
            partial_filled_flag = True
            return
        elif o_state != "filled":
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
        print("ExecuteError in handle_order_update", e, inspect.stack()[1][4])

def cancel_order_and_restore_system(symbol, orderid):
    order_list = []
    order_list.append(orderid)
    batch_cancel_orders(symbol, order_list)
    if db_enabled:
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

    if cur_qsize>= 2:
        tmp_percent = (minute_price_q.queue[cur_qsize-1]-minute_price_q.queue[cur_qsize-2])*100/minute_price_q.queue[cur_qsize-2]
        result_str = "2:%.2f%%"%(tmp_percent)

    if cur_qsize>= 3:
        tmp_percent = (minute_price_q.queue[cur_qsize-1]-minute_price_q.queue[cur_qsize-3])*100/minute_price_q.queue[cur_qsize-3]
        result_str += " 3:%.2f%%"%(tmp_percent)

    if cur_qsize>= 4:
        tmp_percent = (minute_price_q.queue[cur_qsize-1]-minute_price_q.queue[cur_qsize-4])*100/minute_price_q.queue[cur_qsize-4]
        result_str += " 4:%.2f%%"%(tmp_percent)

    if cur_qsize>= 5:
        five_percent = (minute_price_q.queue[cur_qsize-1]-minute_price_q.queue[cur_qsize-5])*100/minute_price_q.queue[cur_qsize-5]
        result_str += " 5:%.2f%%"%(five_percent)
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
        i += 1

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
        i += 1

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

def handle_buy_order(symbol, price, usdt_amount):
    global not_found_in_local_DB_send_email
    #price = int( price*price_precision)/price_precision #it will cause price different later
    usdt_bal = float(get_trade_balance("usdt"))
    buy_amount = usdt_amount
    if usdt_amount > usdt_bal and usdt_bal < 50:
        printme_warning("usdt balance is %f, less than required value %f !"% (usdt_bal, usdt_amount))
        return False
    elif usdt_amount > usdt_bal and usdt_bal > 50:
        buy_amount = usdt_bal

    total_num = int((buy_amount/ price )*amount_precision)/amount_precision
    ret, order_id, max_size = create_buy_order(symbol, price, total_num)
    if ret:
        not_found_in_local_DB_send_email = False
        if db_enabled:
            insert_into_db(order_id, symbol, buy_db_flag, price, total_num, db_program_id)
            printme_warning("creatd order id %s in local db!"% (order_id))
    return ret

def handle_sell_order(symbol, price, usdt_amount, buy_price):
    global not_found_in_local_DB_send_email
    global trade_fee_deduct_value
    global trade_fee_deduct_from_symbol

    #price = int(price*price_precision)/price_precision
    #buy_price = int(buy_price*price_precision)/price_precision
    if trade_fee_deduct_from_symbol:
        total_num = int((usdt_amount*(1-trade_fee_deduct_value)/buy_price)*amount_precision)/amount_precision
    else:
        total_num = int((usdt_amount/buy_price)*amount_precision)/amount_precision
    account_bal = float(get_trade_balance(balance_name))
    account_bal = int(account_bal*amount_precision)/amount_precision

    if account_bal < total_num:
        total_num = account_bal
    
    ret, order_id = create_sell_order(symbol, price, total_num)
    if ret:
        not_found_in_local_DB_send_email = False
        if db_enabled:
            insert_into_db(order_id, symbol, sell_db_flag, price, total_num, db_program_id)
            printme_warning("creatd order id %s in local db!"% (order_id))
    return ret

def get_previous_price(price_list):
    if len(price_list):
        buy_price = price_list[len(price_list)-1]
    else:
        buy_price = 0
    return buy_price

def loop_handle():

    last_price = get_current_price('btcusdt')
    while (1):
        current_price = get_current_price('btcusdt')
        if current_price == 0:
            time.sleep(1)
            continue
        elif last_price - current_price >= 300:
            #report
            send_email("BTC price: -- " + "%.1f <-- %.1f "%(current_price, last_price), "no content")
            last_price = current_price

        elif current_price - last_price >= 300:
            #report
            send_email("BTC price: ++ " + "%.1f <-- %.1f "%(current_price, last_price), "no content")
            last_price = current_price

        print("btc price", current_price, last_price)
        time.sleep(loop_time)


if __name__ == '__main__':

    threading.Thread(target=loop_handle).start()




