import db_sock
from sim_get import *
import uuid
import re

def sim_buy_market_order(symbol, price, amount):
    #  request : ticker, buy_amount
    #      ex) : "KRW-XRP", 6000
    # response : uuid, volume, buy_price, buy_amount
    #      ex) : "uuid", 10, 600, 6000
    if re.match(r'^[A-Z]{3}-[A-Z]{3}$', symbol):
        print(f"{symbol} is OK")
    else:
        print(f"{symbol} is No")

    if isinstance(amount, int) and amount >= 5000:
        print(f"{amount} is OK")
    else:
        print(f"{amount} is No, type is int and more than 5000")

    try:
        t_uuid = str(uuid.uuid4())
        volume = amount/price
        req = {
            'symbol':symbol,
            'uuid':t_uuid,
            'price':price,
            'amount':amount,
            'volume':volume
        }
        # sim_wallet 계좌에서 잔액 -, 보유코인 +, 평단가 수정
        # sim_order_info 정보에 buy 주문 정보 입력
        res, msg = db_sock.market_buy(req)
        if res == 0:
            return msg
    except Exception as e:
        print(f"Error : buy_market_order | {e}")
        res = 0
    return res


coin = 'KRW-XRP'
cur_price = GET_CUR_PRICE(coin,7465)
print(sim_buy_market_order(coin, cur_price, 6000))