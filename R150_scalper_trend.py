import pyupbit
from logging import handlers
import logging
from datetime import datetime
import time
import pybithumb
import math
import os

### 거래할 코인 symbol
coin = "KRW-XRP" 

### 시작금액
start_money = 150000

### 현금이 N% 남으면 마지막 지정가 매도주문
last_sell_order = 10

### 마지막 지정가 매도 주문 수익률
profitPer = 1.06

### API 키 파일 참조
with open("key.txt") as f:
    access_key, secret_key = [line.strip() for line in f.readlines()]

### 업비트 연동
upbit = pyupbit.Upbit(access_key, secret_key) 

### 로깅 설정 부분
LogFormatter = logging.Formatter('%(message)s')
today_ymd=datetime.today().strftime("%Y%m%d")

### 저장할 로그 파일 물리경로 지정
#logPath= "C:\\Users\\PHM\\Desktop\\git\\trace" # hansol
logPath= "C:\\Users\\a\\Desktop\\upbit_python\\scalper\\trace"

### 로그 파일명 지정 (00시 기준으로 '파일명.날짜' 형식으로 백업됨)
logFile="scalper"
LOGPATH=os.path.join(logPath, logFile)

LogHandler = handlers.TimedRotatingFileHandler(filename=LOGPATH, when='midnight', interval=1, encoding='utf-8')
LogHandler.setFormatter(LogFormatter)
LogHandler.suffix = "%Y%m%d"

Logger = logging.getLogger()
Logger.setLevel(logging.INFO)
Logger.addHandler(LogHandler)

### log 출력함수
###  [INPUT] log("TR", a, b, "c = "+c)
### [OUTPUT] TR|2023-06-22 06:13:27| GET_BUY_AVG| KRW-XRP
def log(level, *args):
    now = datetime.now()
    real_time = now.strftime('%Y-%m-%d %H:%M:%S')

    if level not in ("TR", "DG", "INFO"):   # 로그레벨 미지정시 에러
        logs = f"TR|{real_time}|Log Level Error|"
        Logger.info(logs)
        return 0

    logs = f"{level}|{real_time}"

    try:
        for i in args:  # log 함수에 인자로 받은 내용을 출력내용에 포함
            i = str(i)
            logs += f"| {i}"
    except Exception as e:
        logs += f"ER({e})"

    Logger.info(logs)   # log 파일에 출력
    return 1
    
###
def log_function_call(func):
    def wrapper(*args, **kwargs):
        params = ", ".join([f"{arg}" for arg in args])  # 인자들을 문자열로 변환
        log("TR",func.__name__,params)  # 호출된 함수명과 파라미터를 로깅
        return func(*args, **kwargs)    # 제공된 인자들로 원본 함수를 호출
    return wrapper

def fetch_data(fetch_func):
    while True:
        res = fetch_func()  # fetch_func() 함수를 호출하여 데이터
        if res is not None: # 가져온 데이터가 None이 아닌 경우 루프를 종료
            break
        time.sleep(0.5) # 데이터를 가져오지 못한 경우 0.5초 동안 대기
    return res

### 로깅에 필요한 함수명 전달
@log_function_call
def GET_QUAN_COIN(ticker, *args):   # 보유 코인수량 리턴
    try:
        res = fetch_data(lambda: upbit.get_balance(ticker)) # 'upbit.get_balance(ticker)' 를 실행하는 lambda 함수를 fetch_data() 함수로 보내 데이터 수신
        log("TR", "Success", res)
    except Exception as e:
        res = 0
        log("TR", "Fail", e)
    return res

@log_function_call
def GET_BUY_AVG(ticker, *args):     # 평균매수가 리턴
    try:
        res = fetch_data(lambda: upbit.get_avg_buy_price(ticker))
        log("TR", "Success", res)
    except Exception as e:
        res = 0
        log("TR", "Fail", e)
    return res

@log_function_call
def GET_CUR_PRICE(ticker, *args):   # 현재가격 리턴
    try:
        res = fetch_data(lambda: pyupbit.get_current_price(ticker))
        log("TR", "Success", res)
    except Exception as e:
        res = 0
        log("TR", "Fail", e)
    return res

@log_function_call
def GET_CASH(ticker, *args):        # 현재 현금보유액 리턴 (미체결 주문액 제외)
    try:
        res = fetch_data(lambda: upbit.get_balance("KRW"))
        log("TR", "Success", res)
    except Exception as e:
        res = 0
        log("TR", "Fail", e)
    return round(res)

@log_function_call
def GET_MARKET_TREND(ticker, price, days_short, days_long):  
    ticker_bithumb = ticker.split('-')[1]   # ticker에서 '-'를 기준으로 분리하여 암호화폐 심볼을 추출 (pybithumb.get_ohlcv 함수 호출시 사용)
    try:
        price_gap = price * 0.01    # 현재가격에 1%인 값을 price_gap으로 설정
        df = fetch_data(lambda: pybithumb.get_ohlcv(ticker_bithumb))    # pybithumb 라이브러리를 사용하여 암호화폐의 OHLCV 데이터 수신
        ma_short = df['close'].rolling(window=days_short).mean()    # 일정 기간(days_short) 동안의 종가 평균값(ma)을 계산
        last_ma_short = ma_short.iloc[-2] + price_gap    # (days_short) 기간 동안의 종가 평균값(ma)에 price_gap을 더한 값을 last_ma로 설정
        trend = None    # 추세(trend)를 초기화
        if price > last_ma_short: 
            trend = "up"    # 현재 가격(price)이 이전 기간의 종가 평균값(last_ma)보다 큰 경우 추세를 "up"으로 설정
        else:
            trend = "down"  # 그렇지 않은 경우 추세를 "down"으로 설정

        """
        기본적으로 'run-up' 및 'up'은 상승 추세로 판단되고, 'down'은 하락 추세로 판단
        단기(days_short)가 상승추세일때 매수가 재조정(현재가격 - 3틱)
        단기(days_short)가 하락추세여도 장기(days_long)가 큰 폭으로 상승한 경우에도 매수가 재조정
        """
        ### 장기 기간(days_long) 동안의 종가 평균값(ma_long)을 계산
        ma_long = df['close'].rolling(window=days_long).mean()
        last_ma_long = round((ma_long.iloc[-2] + price_gap)*1.2)   # 이전 기간의 종가 평균값(ma_long)에 price_gap을 더한 값에 1.2를 곱하여 last_ma_long으로 설정

        if price > last_ma_long:
            trend="run-up"  # 현재 가격(price)이 이전 기간의 종가 평균값(last_ma_long)보다 큰 경우 추세를 "run-up"으로 설정
            last_ma_short = last_ma_long # 별뜻없음 그냥 로깅 편하게 하려고
        log("TR", "Cur Price:"+str(price), "Trend price:"+str(last_ma_short),"Trend:"+trend)
        return trend
    except Exception as e:
        # 에러발생시 전체 변수 로깅
        log("TR", "Fail", e, "ticker: " + str(ticker), "days: " + str(days_short), "price: " + str(price), "price_gap: " + str(price_gap), "ma5: " + str(ma_short), "last_ma5: " + str(last_ma_short), "trend: " + str(trend), "days_long: " + str(days_long), "ma20: " + str(ma_long), "last_ma20: " + str(last_ma_long))
        return 0

@log_function_call
def GET_ORDER_INFO(ticker, *args):  # 주문 내역 리턴 (uuid & bid or ask & 주문가 & 주문수량)
    try:
        ret = fetch_data(lambda: upbit.get_order(ticker))
        if "error" in ret[0]:
            log("TR", "Error", ret[0])
            res = 0
        else:
            for i in range(0,len(ret)): # 주문 내역이 여러개인 경우 모두 출력
                if ret[i]['side'] == 'ask' or 'bid':
                    res = ret[i]['uuid'] +"&"+ ret[i]['side'] +"&"+ ret[i]['price'] +"&"+ ret[i]['volume']
                    log("TR", "Success", res)
    except IndexError as ie:
        res = 2
        log("TR", "Try Last Sell Order", ie)
    except Exception as e:
        res = 0
        log("TR", "Fail", e)
    return res  # 조회된 주문내역 중 가장 마지막(최근) 주문내역 리턴

@log_function_call
def GET_ORDER_STATE(uuid):   # 주문 상태 리턴 (오류:error / 대기:wait / 완료:done)
    try:
        retn = fetch_data(lambda: upbit.get_order(uuid, state='wait'))
        if "error" in retn:
            log("TR", "Error", retn)
            res = 0
        else:
            res = retn['state']
            log("TR", "Success", res)
    except Exception as e:
            res = 0
            log("TR", "Fail", e)
    return res

def calculate_trade_unit(cash):
    if cash <= 600000:
        return 6000
    elif 500000 < cash <= 1000000:
        return 10000
    elif 1000000 < cash <= 1500000:
        return 15000
    elif 1500000 < cash <= 2000000:
        return 20000
    elif 2000000 < cash <= 3000000:
        return 25000
    elif 3000000 < cash <= 4000000:
        return 35000
    elif 4000000 < cash <= 8000000:
        return 50000
    elif 8000000 < cash:
        return 100000
    else:
        return 0

def calculate_tick_unit(price): # 코인 가격에 따른 tick 단위 지정
    if price < 1000:
        return 1
    elif price < 10000:
        return round(price * 0.0015)
    elif price < 100000:
        return round(price * 0.002)
    elif price < 500000:
        return round(price * 0.0025)
    elif price < 1000000:
        return round(price * 0.003)
    else:
        return round(price * 0.0035)

@log_function_call
def ORDER_CANCLE(ticker, *args):    # 주문 취소 기능. 수동 사용
    ret = GET_ORDER_INFO(ticker)
    try:
        order_uuid = ret.split('&')[0]
        result = upbit.cancel_order(order_uuid)
        res = 1 
        log("TR", "Success", result)
    except Exception as e:
        res = 0 
        log("TR", "Fail", e)
    return res

@log_function_call
def ORDER_BUY_MARKET(ticker, buy_amount):   # 시장가 매수 주문 후 결과 리턴(uuid를 포함한 매수 정보)
    if buy_amount < 5000:   # 매수 금액이 5000보다 작은 경우 실패(업비트 최소주문 단위)
        log("TR", "Fail",ticker, buy_amount,"amount is better than 5000")
        return 0
    try:
        res = upbit.buy_market_order(ticker,buy_amount) # 매수주문 결과를 res 변수에 저장
        if 'error' in res:
            log("TR","Error", ticker, buy_amount, res)
            res = 0
            return res
        log("TR", "Success", ticker, buy_amount, res)
    except Exception as e:
        res = 0 
        log("TR", "Fail",ticker, buy_amount, e)
    return res

@log_function_call
def ORDER_SELL_MARKET(ticker, *args):   # 시장가 매도 주문 결과 리턴 (uuid를 포함한 정보)
    try:
        sell_quan = GET_QUAN_COIN(ticker)   # 현재 보유중인 수량 조회
        res = upbit.sell_market_order(ticker,sell_quan) # 현재 보유중인 코인 일괄매도
        if 'error' in res:
            log("TR","Error", ticker, sell_quan, res)
            res = 0
            return res
        log("TR", "Success", ticker, sell_quan, res)
    except Exception as e:
        log("TR", "Fail", ticker, sell_quan, e)
        res = 0 
    return res
    
@log_function_call
def ORDER_SELL_LIMIT(ticker, profit, *args):    # 지정가 매도 주문 결과 리턴 (지정한 Minimum Cash 가격에 도달한 경우 진행)
    if profit < 1.01:
        log("TR", "Check your profiePer Value", profit)
    try:
        vol = math.floor(upbit.get_balance(ticker))     # 매도 수량 지정(소수점 첫째 자리에서 내림계산)
        buy_avg_price = math.floor(profit * GET_BUY_AVG(ticker))      # 평균 매수가를 매도 주문 가격으로 지정
        res = upbit.sell_limit_order(ticker, buy_avg_price, vol)    
        if 'error' in res:
            log("TR","Error", ticker, profit, buy_avg_price, res)
            return res
        log("TR", " Success", ticker, profit, buy_avg_price,res)
        res = 1
    except Exception as e:
        log("TR", "Fail", ticker, profit, buy_avg_price, e)
        res = e
    return res

def run(chk_run):
    if chk_run == 0:
        ### 초기변수 설정
        rise_chk = 0
        chk_sell_order = 0
        chk_15m_timer = 0
        cur_coin = 0.0
        cur_cash = 0.0
        cur_price = 0.0
        buy_amount = 0.0
        buy_price = 0.0
        sell_amount = 0.0
        sell_price = 0.0
        min_cash = 0.0

        cur_price = GET_CUR_PRICE(coin)                     # 현재 코인 가격 조회
        one_tick = calculate_tick_unit(cur_price)           # 호가(최소 변동폭) 단위 조회
        cur_cash = GET_CASH(coin)                           # 현재 보유 현금 조회
        cur_coin = GET_QUAN_COIN(coin)                      # 현재 보유 코인 조회

        if cur_cash < 1:
            log("DG","Check the ash ", str(cur_cash))
            time.sleep(10)
            return 0
        
        if cur_coin * cur_price >= one_tick:                                    #
            sell_price = round(GET_BUY_AVG(coin) * 1.03)    # 현재 보유 코인이 2개 이상인 경우 매도 가격 체크
            log("DG","Initial Sell Price : "+str(sell_price), "Current Quntity Coin : "+str(cur_coin))
        else:                                               # 
            sell_price = 0.0         
        
        buy_price = cur_price - (one_tick * 3)              # 최초 매수가격은 현재 가격에서 3틱을 뺀 값으로 지정
        buy_amount = calculate_trade_unit(cur_cash)         # 보유 현금에 비례하여 1회당 매수 금액 지정
        if buy_amount == 0:
            log("DG","calculate_trade_unit() Error")
            time.sleep(10)
            return 0
        before_buy_price = buy_price                        # -아직 미사용-

    """
    chk_run value
    0 : Reset the Settings. (not yet)
    1 : Trade Start
    2 : Program Exit
    """
    chk_run = 1
    time.sleep(1)

    while chk_run == 1:
        ### 현재 보유 현금이 0원인 경우는 업비트와의 통신에 문제가 있다고 판단하여 10초뒤 재실행
        cur_cash = GET_CASH(coin)
        if cur_cash == 0:
            log("DG","The balance is confirmed as $0.")
            time.sleep(10)
            continue

        ### 보유 현금액이 min_cash 미만이 되면 일괄매도 진행
        cur_cash = GET_CASH(coin)
        if cur_cash < min_cash:     
            log("DG","Cash on hand is too low.")

        ### 현재 코인의 가격이 0원인 경우 업비트와의 통신에 문제가 있다고 판단 하여 10초뒤 재실행
        cur_price = GET_CUR_PRICE(coin) 
        if cur_price == 0:
            log("DG","Current Price small than 1.")
            time.sleep(10)
            continue

        cur_coin = GET_QUAN_COIN(coin) 
        if cur_coin * cur_price <= one_tick:
            sell_price = 0.0
        
        one_tick = calculate_tick_unit(cur_price)

        if chk_15m_timer != 0:
            if int(time.strftime("%M")) % 15 == 0:  # 매시 15분 마다 타이머 초기화
                log("INFO","Check Timer reset")
                chk_15m_timer = 0

        min_cash = round((cur_cash + (cur_coin * cur_price)) * last_sell_order/100)  # 최초 금액 대비 (10%) 가 되면 매수중지
        if cur_cash > min_cash:
            try:
                wallet = round(cur_cash + (cur_coin * cur_price))
                log("DG","WALLET : " + str(wallet) , "ACCOUNT : " + str(round(cur_cash)),"COIN_" + str(coin) + " : " + str(cur_coin))

                trend = GET_MARKET_TREND(coin, cur_price, 3, 20)    # 단기를 3일, 장기를 20일 으로 평균 종가 계산 후 상승, 하락 추세 판단
                if  trend == "up":
                    log("DG","The price is high. Reset Buy price.")
                    rise_chk = 1
                elif trend == "run-up":
                    log("DG","The price is Crazy run-up. Reset Buy price.")
                    rise_chk = 1

                if rise_chk == 1:
                    buy_price = cur_price - (one_tick * 3)
                    log("INFO","One Tick : " + str(one_tick),"Cur Price : " + str(cur_price),"Buy Price : "+str(buy_price))
                    rise_chk = 0    

                log("DG","CUR_PRICE : " + str(cur_price), "BUY_PRICE  : " + str(buy_price))
                if cur_price < buy_price:   # 가격이 지정한 매수가 밑으로 내려오면 매수 진행
                    if chk_15m_timer > 3:   # 15분 동안 매수 3회 제한
                        buy_price = cur_price - (one_tick * 3)
                        log("DG","Purchased more than 3 times in 15 minutes.")
                    else:
                        res = ORDER_BUY_MARKET(coin, buy_amount)
                    time.sleep(1)

                    if res != 0:
                        chk_15m_timer += 1  # 매수 체결시 체크타이머 +1 (15분 마다 0으로 초기화)
                        log("INFO","Check Timer : " + str(chk_15m_timer))
                        buy_price = cur_price - (one_tick * 3)
                        sell_price = round(GET_BUY_AVG(coin) * 1.03)    # 평균 매수가 +n% 가격을 매도가로 설정
                        log("DG", "BUY ORDER " + str(coin)+ " : " + str(cur_price), "AMOUNT : " + str(buy_amount))

                log("DG","CUR_PRICE : " + str(cur_price), "SELL_PRICE : " + str(sell_price))
                if cur_price >= sell_price and (cur_coin * cur_price) > 6000:   # 가격이 매도가보다 높고, 매도 금액이 최소 주문 단위인 6000원 초과인 경우 매도 진행
                    res = ORDER_SELL_MARKET(coin)
                    time.sleep(1)

                    if res != 0:
                        sell_amount = res['executed_volume']
                        log("DG", "SELL ORDER " + str(coin) + " : " + str(sell_price), "AMOUNT : " + str(sell_amount))
                        sell_price = 0.0

                margin = round(wallet-start_money)  # 수익금
                margins = round((margin/start_money)*100,2) # 수익률
                log("DG", "Initial Money : " + str(start_money), "Margin : " + str(margin) + " ("+ str(margins)+" %)")
            except Exception as e:
                log("DG", "Margin CALC Fail",e)

        else:   # 매도가 이뤄지지 않아 보유 현금액의 n%가 되었을 때 (평단가*k%)값으로 매도주문 후 대기
            try:
                order_info = GET_ORDER_INFO(coin)
                if order_info == 2: # 조회는 성공했으나 주문이 없는 경우
                    last_order_res = ORDER_SELL_LIMIT(coin,profitPer)
                    log("INFO", "Last Sell Order Result" + str(last_order_res))
                elif order_info == 0:
                    log("DG", "Fail to GET ORDER INFO")
                    time.sleep(5)
                    continue
                else:
                    order_info = GET_ORDER_INFO(coin).split('&')
                    last_order_res = 1
                
                if last_order_res == 1:     
                    log("DG", "Last Order Success ", last_order_res)
                    log("DG", "UUID   : "+order_info[0])
                    log("DG", "PRICE  : "+order_info[2])
                    log("DG", "VOLUME : "+order_info[3])
                    chk_sell_order = 1  # 매도가 완료될 때 까지 대기하는 반복문을 실행
                    time.sleep(10)
                else:
                    log("DG", "Last Order Fail", last_order_res)
                    continue
                
            except Exception as e:
                log("DG", "Fail ", e)


        while chk_sell_order == 1:
            try:
                tmp = GET_ORDER_INFO(coin)
                # 조회는 성공했으나 주문 정보가 없는 경우
                if tmp == 2:
                    chk_sell_order = 0
                    break
                # 에러
                elif tmp == 0:
                    log("DG", "Fail","GET ORDER INFO Return")
                    chk_sell_order = 0
                    time.sleep(10)
                    continue
                else:
                    order_info = tmp.split('&')     # 주문 정보 파싱

                order_uuid = order_info[0]
                order_status = GET_ORDER_STATE(order_uuid)

                if order_status == 'wait':
                    log("DG", "Cur Price :" + GET_CUR_PRICE(coin), "Sell price : " + order_info[2])
                    log("DG", "Sell Order Status : " + order_status)
                else:
                    log("DG", "Sell Order Status : " + order_status)
                    chk_run = 0
                    chk_sell_order = 0
                time.sleep(60)

            except Exception as e:
                log("DG", "Fail",e)
                chk_run = 2
                chk_sell_order = 0

        time.sleep(10)

    if chk_run == 2:
        log("DG","Trade Exit.")

### START ###
if __name__ == '__main__':
    while True:
        run(0)
