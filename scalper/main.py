from logger import log
from scalper.sim_get import *
from trade_calculator import *

def run(chk_run):
    if chk_run == 0:

        ### 초기변수 설정
        #coin = 'KRW-BTC'
        #coin = 'KRW-ETH'
        coin = 'KRW-XRP'
        start_money = 1,000,000
        #start_money = GET_CASH(coin)
        rise_chk = 0    # 1 : UP / 0 : DOWN
        chk_sell_order = 0
        chk_15m_timer = 0
        cur_coin = 0.0
        cur_cash = 0.0
        cur_price = 0.0
        buy_amount = 0.0
        buy_price = 0.0
        sell_amount = 0.0
        sell_price = 0.0

        cur_cash = GET_CASH(coin)                           # 현재 보유 현금 조회
        if cur_cash < 1:
            log("DG","GET_CASH() Error ", str(cur_cash))
            #time.sleep(10)
            return 0
        cur_coin = GET_QUAN_COIN(coin)                      # 현재 보유 코인 조회
        if cur_coin > 2:                                    #
            sell_price = round(GET_BUY_AVG(coin) * 1.03)    # 현재 보유 코인이 2개 이상인 경우 매도 가격 체크
            log("DG","Initial Sell Price : "+str(sell_price), "Current Quntity Coin : "+str(cur_coin))
        else:                                               # 
            sell_price = 0.0                                #  
        cur_price = GET_CUR_PRICE(coin)                     # 현재 코인 가격 조회
        #cur_price = get_price(chk_next=0)
        one_tick = calculate_tick_unit(cur_price)           # 호가(최소 변동폭) 단위 조회
        buy_price = cur_price - (one_tick * 3)              # 최초 매수가격은 현재 가격에서 3틱을 뺀 값으로 지정
        buy_amount = calculate_trade_unit(cur_cash)         # 보유 현금에 비례하여 1회당 매수 금액 지정
        #log("INFO","Cur Price : " + str(cur_price),"One Tick : " + str(one_tick), "Buy Price : " + str(buy_price), "Buy Amount : " + str(buy_amount))
        if buy_amount == 0:
            #log("DG","calculate_trade_unit() Error")
            #time.sleep(10)
            return 0
        before_buy_price = buy_price                        # -아직 미사용-

    """
    chk_run value
    0 : Reset the Settings. (not yet)
    1 : Trade Start
    2 : Program Exit
    """
    chk_run = 1
    #time.sleep(1)

    if(chk_run == 1):
        log("TR","start")

    while chk_run == 1:
        time.sleep(5)
        cur_cash = GET_CASH(coin)
        if cur_cash == 0:   # 현재 보유 현금이 0원인 경우는 업비트와의 통신에 문제가 있다고 판단하여 10초뒤 재실행
            #log("DG","The balance is confirmed as $0.")
            time.sleep(10)
            continue

        if int(time.strftime("%M")) % 15 == 0:  # 매시 15분 마다 타이머 초기화
            chk_15m_timer = 0

        min_cash = round((cur_cash + (cur_coin * cur_price)) * 10/100)  # 최초 금액 대비 (10%) 가 되면 매수중지
        if cur_cash > min_cash:
            try:
                cur_price = GET_CUR_PRICE(coin) 
                #cur_price = get_price(chk_next=1)

                ### 현재 코인의 가격이 0원인 경우 업비트와의 통신에 문제가 있다고 판단 하여 10초뒤 재실행
                if cur_price == 0:
                    #log("DG","Current Price small than $1.")
                    cur_price = 1
                    if buy_price > 1:
                        before_buy_price = buy_price
                    buy_price = 0
                    #time.sleep(10)
                    continue

                if buy_price == 0:
                    buy_price = before_buy_price
                    #buy_price = cur_price - (one_tick * 3)

                cur_cash = GET_CASH(coin)
                if cur_cash < min_cash:     # 보유 현금액이 min_cash 미만이 되면 일괄매도 진행
                    log("DG","Cash on hand is too low.")
                    continue

                cur_coin = GET_QUAN_COIN(coin) 
                if cur_coin < 2:
                    sell_price = 0.0

                wallet = round(cur_cash + (cur_coin * cur_price))
                #log("DG","WALLET : " + str(wallet) , "ACCOUNT : " + str(round(cur_cash)),"COIN_" + str(coin) + " : " + str(cur_coin))

                trend = GET_MARKET_TREND(coin, cur_price, 3, 20)
                if  trend == "up":
                    #log("DG","The price is high. Reset Buy price.")
                    rise_chk = 1
                elif trend == "run-up":
                    #log("DG","The price is Crazy run-up. Reset Buy price.")
                    rise_chk = 1

                if rise_chk == 1:
                    one_tick = calculate_tick_unit(cur_price)
                    #log("INFO","One Tick : " + str(one_tick),"Cur Price : " + str(cur_price))
                    buy_price = cur_price - (one_tick * 3)
                    rise_chk = 0    

                #log("DG","CUR_PRICE : " + str(cur_price), "BUY_PRICE  : " + str(buy_price))
                if cur_price < buy_price:
                    old_buy_price = buy_price

                    one_tick = calculate_tick_unit(cur_price)
                    #log("INFO","One Tick : " + str(one_tick),"Cur Price : " + str(cur_price))
                    if chk_15m_timer > 3:
                        buy_price = cur_price - (one_tick * 3)
                        #log("DG","Purchased more than 3 times in 15 minutes.")
                    else:
                        #res = ORDER_BUY_MARKET(coin, buy_amount)
                        res = sim_Buy_order(coin, buy_amount)
                    time.sleep(1)

                    buy_price = cur_price - (one_tick * 3) 

                    if res != 0:
                        #chk_15m_timer += 1  # 매수 체결시 체크타이머 +1 (15분 마다 0으로 초기화)
                        #log("INFO","Check Timer : " + str(chk_15m_timer))
                        buy_price = cur_price - (one_tick * 3)
                        sell_price = round(GET_BUY_AVG(coin) * 1.03)    # 평균 매수가 +n% 가격을 매도가로 설정
                        buy_price = cur_price - (one_tick * 3)
                        buy_avg_price = round(GET_BUY_AVG(coin))
                        sell_price = buy_avg_price * 1.03
                        cur_balance_cash = GET_CASH(coin)
                        cur_balance_coin = GET_QUAN_COIN(coin)
                        sim_wallet_update(name=coin, price=cur_price, trend=trend, trend_price=999, buy_price=old_buy_price, sell_price=sell_price, buy_avg_price=buy_avg_price, cur_balance_cash=cur_balance_cash, cur_balance_coin=cur_balance_coin)
                        log("DG", "BUY " + str(coin)+ " : " + str(cur_price), "AMOUNT : " + str(buy_amount))
                    else: 
                        log("DG", "BUY FAIL", res)

                #log("DG","CUR_PRICE : " + str(cur_price), "SELL_PRICE : " + str(sell_price))
                # 시장가 매도 진행
                if cur_price >= sell_price and (cur_coin * cur_price) > 6000:   # 가격이 매도가보다 높고, 매도 금액이 최소 주문 단위인 6000원 초과인 경우 매도 진행
                    #res = ORDER_SELL_MARKET(coin)
                    res = sim_Sell_order(coin)
                    time.sleep(1)
                    sell_price = 0.0
                    if res != 0:
                        sell_amount = res['executed_volume']
                        log("DG", "SELL " + str(coin) + " : " + str(sell_price), "AMOUNT : " + str(sell_amount))
                        sell_price = 0.0
                        sim_wallet_update(name=coin, price=cur_price, trend=trend, trend_price=999, buy_price=0, sell_price=sell_price, buy_avg_price=0, cur_balance_cash=cur_balance_cash, cur_balance_coin=0)
                        margin = round(wallet-start_money)  # 수익금
                        margins = round((margin/start_money)*100,2) # 수익률
                        #log("DG", "Initial Money : " + str(start_money), "Margin : " + str(margin) + " ("+ str(margins)+" %)")
                        log("DG","BUY : "+str(buy_price)+" SELL : "+str(sell_price)+ " Margin : " + str(margin) + " ("+ str(margins)+" %)")
                    else:
                        log("DG", "SELL FAIL", res)
            except Exception as e:
                log("DG", "Fail",e)

        else:   # 매도가 이뤄지지 않아 보유 현금액의 n%가 되었을 때 (평단가*1.02)값으로 매도주문 후 대기
            try:
                last_order_res = sim_limit_Sell_order(coin)
                log("DG", "result", last_order_res)
                if last_order_res == 1: 
                    #order_info = GET_ORDER_INFO(coin).split('&') 
                    order_info = GET_ORDER_INFO(coin) 
                    log("DG", "Last Order Success ")
                    log("DG", "UUID   : "+order_info[0])
                    log("DG", "PRICE  : "+order_info[2])
                    log("DG", "VOLUME : "+order_info[3])
                    chk_sell_order = 1  # 매도가 완료될 때 까지 대기하는 반복문을 실행
                else:
                    log("DG", "Fail", last_order_res)
                    continue
                
            except Exception as e:
                log("DG", "Fail ", e)

        while chk_sell_order == 1:
            try:
                tmp = GET_ORDER_INFO(coin)
                if tmp != 0:
                    #order_info = tmp.split('&')     # 주문 정보 파싱
                    order_info = tmp     # 주문 정보 파싱
                elif tmp == 0:
                    log("DG", "Fail to Get Order Info..")
                    time.sleep(10)
                    continue
                else:   # 예외 상황 방생시 코드 종료
                    log("DG", "Fail","GET_ORDER_INFO Return : " + str(tmp))
                    chk_run = 2
                    chk_sell_order = 0
                    #time.sleep(1)
                    continue
                #order_uuid = order_info[0]
                order_uuid = str(order_info['uuid'])
                order_status = GET_ORDER_STATE(order_uuid)

                if order_status == 'wait':
                    log("DG", "Sell Order Status : wait")
                elif order_status == 'done' or order_status == '0':
                    log("DG", "Sell Order Status : " + order_status)
                    chk_run = 0 
                    chk_sell_order = 0
                    buy_avg_price = GET_BUY_AVG(coin)
                    sell_price = round(GET_BUY_AVG(coin)*1.03)
                    cur_balance_cash = GET_CASH(coin)
                    cur_balance_coin = GET_QUAN_COIN(coin)
                    sim_wallet_update(name=coin, price=cur_price, trend='limit', trend_price=999, buy_price=1, sell_price=sell_price, buy_avg_price=buy_avg_price, cur_balance_cash=cur_balance_cash, cur_balance_coin=cur_balance_coin)
                else:
                    log("DG", "Sell Order Status : " + order_status)
                    chk_run = 2
                    chk_sell_order = 0
                #time.sleep(60)
            except Exception as e:
                log("DG", "Fail",e)
                chk_run = 2
                chk_sell_order = 0

        #time.sleep(10)
            

    """
    test
    """
    if chk_run == 2:
        log("DG","Trade Exit.")

### START ###
if __name__ == '__main__':
    while True:
        run(0)
