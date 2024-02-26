import socket
import json
from sim_get import *

        # req = {
        #     'uuid':t_uuid,
        #     'price':price,
        #     'amount':amount,
        #     'volume':volume
        # }
def market_buy(req):
    symbol = req['symbol']
    uuid = req['uuid']
    price = req['price']
    amount = req['amount']
    volume = req['volume']
    
    # 1) 주문 잔액 체크
    cur_cash = GET_CASH()
    if cur_cash <= amount:
        return 0, 'CASH is not enough'

    # 2) sim_order_info 주문 체결
    try:
        data_to_insert = {
            "query_type": "insert",
            "table_name": "sim_order_info",
            "data":{
                "t_uuid":uuid,
                "name":symbol,
                "price":price,
                "amount":amount,
                "volume":volume,
                "type":'buy',
                "last_order":'none'
            }
        }
        res = db_sock(data_to_insert)
    except Exception as e:
        print(e)
        return 1, e
    
    # 3) sim_wallet 정보 수정

    return 1, res

def db_sock(data):
    # 서버 설정
    server_address = "13.125.245.156"  # 서버의 실제 IP 주소 또는 도메인 이름
    server_port = 59507  # 서버 포트 번호

    # 서버에 연결
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))

    try:
        # 데이터를 JSON 형식으로 직렬화
        request_json = json.dumps(data)

        # 서버에 요청 보내기
        client_socket.send(request_json.encode("utf-8"))

        # 서버로부터 응답 받기
        response_json = client_socket.recv(1024).decode("utf-8")

        return response_json

    except Exception as e:
        print(f'error: {e}')
        return None

    finally:
        # 클라이언트 소켓 닫기
        client_socket.close()