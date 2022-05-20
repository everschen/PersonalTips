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
import inspect

# import pymysql
# pymysql.install_as_MySQLdb()

symbol = "btc3lusdt"
symbol_bal= 'btc3l'
#symbol_bal= 'eth3l'

account_id = 23455585

price_difference = 0.6

price_precision = 100 #price 价格精度
amount_precision = 10000

loop_wait_time = 1*60

price_points = []
state_points = {}

g_api_key = 'xxx'
g_secret_key = 'xxx'

lock = threading.Lock()

db = MySQLdb.connect("localhost", "root", "abcd.12345", "ecoin_system", charset='gb2312' )

def make_precision(value, precision):
    return int(value*precision)/precision

#buy=1, sell=2
def check_order_in_db(symbol, buy_sell, price):
    cursor = db.cursor()
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
    cursor = db.cursor()
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
    cursor = db.cursor()
    sql = "delete from trade_order \
            where orderid=%d"% (orderid)
    try:
        cursor.execute(sql)
        db.commit()
        printme("order id %d is removed from local db"%(orderid))
    except:
        db.rollback()




def printme( str, new_line=False):
    if new_line:
        cur_time = time.strftime("\n%Y-%m-%d %H:%M:%S ", time.localtime())
    else:
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
            #print("order:", order_id[0], order_type[0], buy_price, sell_price, current_price)
            if (order_type[0] == "buy-limit"):
                if current_price == buy_price:
                    return True,True,int(order_id[0]),float(amount[0])
            else:
                if current_price == sell_price:
                    return True,False,int(order_id[0]),float(amount[0])
    except:
        print("ExecuteError:", inspect.stack()[1][4])

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
                #print("order:", order_id[0], order_type[0], buy_price, sell_price, current_price)
                if (order_type[0] == "buy-limit"):
                    if current_price == buy_price:
                        return True,True,int(order_id[0]),float(amount[0])
                else:
                    if current_price == sell_price:
                        return True,False,int(order_id[0]),float(amount[0])
        except:
            print("ExecuteError:", inspect.stack()[1][4])
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
        print("ExecuteError:", inspect.stack()[1][4])
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
        print("ExecuteError:", inspect.stack()[1][4])

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
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
        order_id = trade_client.create_order(symbol=symbol, account_id=account_id, order_type=OrderType.BUY_LIMIT, source=OrderSource.API, amount=amount, price=price)
        printme("created BUY order id : {id}".format(id=order_id))
        return True, order_id, 0
    except Exception as e:
        print("ExecuteError:", e)
        max_size = 0
        # if "order-holding-limit-failed" in e:
        #     max_size = re.findall("\d+\.*\d*", e)
        return False, 0, max_size

def create_sell_order(symbol, price, amount):
    try:
        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
        order_id = trade_client.create_order(symbol=symbol, account_id=account_id, order_type=OrderType.SELL_LIMIT, source=OrderSource.API, amount=amount, price=price)
        printme("created SELL order id : {id}".format(id=order_id))
        return True, order_id
    except Exception as e:
        print("ExecuteError:", e, inspect.stack()[1][4])
        return False, 0

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
        print("ExecuteError:", inspect.stack()[1][4])
    return 0.0 

def get_trade_balance():
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
            order_type = get_value(symbol_bal, a._buff)
            #print("t", order_type)
            if len(order_type) and order_type[0] == symbol_bal:
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
    sell_price = make_precision(sell_price, price_precision)
    trade_bal = float(get_trade_balance())
    sell_amount = each_usdt_amount / buy_price
    sell_amount = make_precision(sell_amount, amount_precision)
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

    if (trade_bal > sell_amount or trade_bal>0.2) and sell_price > current_price and last_state_price ==1:
        #only after buy then can sell, so the last state should be 1 if want to sell
        if trade_bal < sell_amount and trade_bal>0.2:
            printme_warning("something like less balance now, what happened? maybe deduct fee cause this issue. trade_bal=%f sell_amount=%f, updated!"%(trade_bal, sell_amount))
            sell_amount = trade_bal
        printme("There are balacne %f of %s, sell %f at price %f first."%(trade_bal, symbol, sell_amount, sell_price))
        total_sell_num = make_precision(sell_amount, amount_precision)
        printme("Total are %f, create sell %f %s at price %.4f now."%(trade_bal, total_sell_num, symbol,sell_price))
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

        total_buy_num = make_precision(use_usdt/ buy_price, amount_precision)
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
        printme_warning("IF not price is low than buy price, then please have a check, trade_bal=%f, sell_amount=%f, current_price=%f, buy_price=%.4f, sell_price=%.4f\n"%(trade_bal, sell_amount, current_price, buy_price, sell_price))

    return False,0,0,0

def update_order_implement(trigger):
    print("\n\n\n")
    current_price = get_current_price(symbol)
    for buy_price in price_points:
        sell_price = buy_price + price_difference
        sell_price = make_precision(sell_price, price_precision)
        printme("[%s] handle price %.4f <-- %.4f (current price)"%(trigger, buy_price, current_price), True)
        execute_result, execute_num = has_orders(symbol)
        if execute_result and execute_num:
            has_exact_order, is_buy, orderid, amount = has_buy_order(symbol, buy_price, sell_price, True)
            #printme("has_buy_order: has_exact_order=%d, is_buy=%d, orderid=%d, amount=%f"%(has_exact_order, is_buy, orderid, amount))
            if has_exact_order and is_buy:
                orderid_in_db = check_order_in_db(symbol, 1, buy_price)
                if orderid_in_db:
                    if orderid_in_db != orderid:
                        printme_warning("order id is different between local=%s and remote=%s!"% (orderid_in_db, orderid))
                else:
                    insert_into_db(orderid, symbol, 1, buy_price, amount)
                    printme_warning("creatd order id %s in local db!"% (orderid))
                printme("[%s] Has BUY order %s ongoing, %.4f <-- %.4f (current price) waiting..."%(trigger, orderid, buy_price, current_price))
                state_points[buy_price] = 1

            elif not is_buy and has_exact_order:
                orderid_in_db = check_order_in_db(symbol, 2, sell_price)
                if orderid_in_db:
                    if orderid_in_db != orderid:
                        printme_warning("order id is different between local=%s and remote=%s!"% (orderid_in_db, orderid))
                else:
                    insert_into_db(orderid, symbol, 2, sell_price, amount)
                printme("[%s] Has SELL order %s ongoing, %.4f <-- %.4f (current price) waiting..."%(trigger, orderid, sell_price, current_price))
                state_points[buy_price] = 2

            else :
                printme_warning("START to create order, is_buy=%d, buy_price=%.4f, sell_price=%.4f"%(is_buy, buy_price, sell_price))
                created_success, buy_sell, orderid, amount = create_my_order(buy_price, sell_price, symbol, each_amount)
                if created_success:
                    insert_into_db(orderid, symbol, buy_sell, buy_price if buy_sell==1 else sell_price, amount)
                    printme_warning("creatd order id %s in local db!"% (orderid))

        elif execute_result and not execute_num:
            created_success, buy_sell, orderid, amount = create_my_order(buy_price, sell_price, symbol, each_amount)
            if created_success:
                insert_into_db(orderid, symbol, buy_sell, buy_price if buy_sell==1 else sell_price, amount)
                printme_warning("creatd order id %s in local db!"% (orderid))

        else:
            printme("most probably failed to execute here")

    printme("each_amount=%.2f, current_prince=%.4f, buy price:%r, Let me sleep for one minute..."%(each_amount, current_price, price_points), True)

    print_current_price_buy_sell_state()
    print("current price:", current_price)
    printme("len(state_points) = %d, len(price_points) = %d"%(len(state_points), len(price_points)))
    price_list = []
    for price in price_points:
        if price not in state_points:
            price_list.append(price)

    if len(price_list):
        print("ISSUE: please check, no state price list:", price_list)
        #send_email("HB: " + "ISSUE some price state goes wrong", ','.join('%s' %id for id in price_list))
    print("=======================================================================================================================")

def handle_order_id(order_id, order_type, price):
    lock.acquire()
    global f_trade_done
    global symbol
    global each_amount
    trade_fee_deduct_from_symbol = False
    trade_fee_deduct_value = 0.002

    print("start to handle order id %d now"%order_id)
    if order_type=="sell-limit":
        buy_price  = price - price_difference
        if trade_fee_deduct_from_symbol:
            total_num = make_precision(each_amount*(1-trade_fee_deduct_value)/buy_price, amount_precision)
        else:
            total_num = make_precision(each_amount/buy_price, amount_precision)

        output_to_log_file(f_trade_done, "%s SELL done: %.4f buy:%.4f diff:%.4f amount=%.4f income=%.1f\n"%(symbol, price, buy_price, price-buy_price, total_num, total_num*(price-buy_price)*6.4*0.998))

    elif order_type=="buy-limit":
        output_to_log_file(f_trade_done, "%s BUY done: %.4f amount=%.4f \n"%(symbol, price, each_amount/price))

    else:
        print("sth wrong? order_type=%s"%order_type)
    lock.release()

def get_first_value(list_value):
    if len(list_value):
        ret = list_value[0].strip()
    else:
        ret=""
    return ret

def handle_order_update(upd_event: 'OrderUpdateEvent'):
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

    update_order_implement("Event")

def loop_handle(self):
    while 1:
        update_order_implement("Loop")
        time.sleep(loop_wait_time)

def error_handler(exception: 'HuobiApiException'):
    send_email("HB: " + "subscribe error happened", exception)


def cancel_order_and_restore_system(symbol, orderid):
    order_list = []
    order_list.append(orderid)
    batch_cancel_orders(symbol, order_list)
    remove_order_in_db(orderid)

def cancel_all_order_in_db():
    cursor = db.cursor()
    #print(symbol, buy_sell, price)
    sql = "SELECT * FROM trade_order \
       WHERE symbol='%s'" % (symbol)
    #print(sql)

    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        id = row[0]
        orderid = row[1]
        db_price = row[4]
        cancel_order_and_restore_system(symbol, orderid)

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
        trade_client.sub_order_update(symbol, handle_order_update)


if __name__ == '__main__':
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # formatter = logging.Formatter("%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
    # ch.setFormatter(formatter)
    # logger = logging.getLogger(__file__)
    # logger.setLevel(logging.DEBUG)
    # logger.addHandler(ch)

    if float(sys.argv[1])==0:
        cancel_all_order_in_db()
        exit(0)

    argnum = len(sys.argv)
    if argnum < 4:
        printme_error("please input parameters, range, monitor_num")
        exit(1)

    start_point = float(sys.argv[1])

    end_point = float(sys.argv[2])
    step = float(end_point - start_point +1)/int(sys.argv[3])
    #step = 30

    for i in range(0, int(sys.argv[3])):
        buy_price_tmp = make_precision(start_point + i*step, price_precision)
        price_points.append(buy_price_tmp)

    price_points = sorted(price_points, key = lambda x:float(x))

    current_price = get_current_price(symbol)
    printme("current_prince=%f, buy price:%r"%(current_price, price_points))

    if argnum == 5:
        total_usdt = float(sys.argv[4])
        each_amount = total_usdt/int(sys.argv[3])

    cur_time = time.strftime("%Y-%m-%d", time.localtime())
    log_file = "log/auto-hunter-trade-done-%s-%s.txt"%(symbol_bal,cur_time)
    f_trade_done = open(log_file, mode='a')

    myLoopHandle(1, "myLoopHandle", each_amount).start()
    time.sleep(2)
    myEventHandle(2, "myEventHandle", each_amount).start()

