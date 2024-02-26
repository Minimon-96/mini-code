import db_sock
import json
import time

"""
opt 
    0 : No where option
    1 : where option int/float
    2 : where option str
"""

### 2024-01-17 OK
### 사용법 : GET_ORDER_INFO(none)
### 출력값 : wait 주문 정보 (TYPE : dict in list)
### 에러시 : exception
def GET_ORDER_INFO(t_uuid):
    table_name = "sim_order_info"
    option_field = "t_uuid"
    option_value = t_uuid
    fields = ["t_uuid", "name", "price", "amount", "last_order", "time"]

    try:
        data = {
            "query_type": "select",
            "table_name": table_name,
            "opt": 2,
            "option_field": option_field,
            "option_value": option_value,
            "fields": fields
        }

        res = db_sock.db_sock(data)
        if res:
            print(f'success: {res} {type(res)}')
            json_data = json.loads(res)
            ret = json_data
            return ret
        else:
            return None

    except Exception as e:
        print(f'error: {e}')
        return e


### 2024-01-17 OK
### 사용법 : GET_ORDER_STATE(symbol)
### 출력값 : 'wait' or 'none' (TYPE str)
### 에러시 : exception
def GET_ORDER_STATE(symbol):
    table_name = "sim_wallet"
    option_field = "name"
    option_value = symbol
    field_key = "last_order"
    fields = ["name", field_key, "time"]

    try:
        data = {
            "query_type": "select",
            "table_name": table_name,
            "opt": 2,
            "option_field": option_field,
            "option_value": option_value,
            "fields": fields
        }

        res = db_sock.db_sock(data)
        if res:
            print(f'success: {res} {type(res)}')
            json_data = json.loads(res)
            ret = json_data[1][field_key]
            return ret
        else:
            return None

    except Exception as e:
        print(f'error: {e}')
        return e

### 2024-01-17 OK
### 사용법 : GET_BUY_AVG(symbol)
### 출력값 : 000.0 (Type : float)
### 에러시 : exception
def GET_BUY_AVG(symbol):
    table_name = "sim_wallet"
    option_field = "name"
    option_value = symbol
    field_key = "buy_avg_price"
    fields = ["name", field_key, "time"]

    try:
        data = {
            "query_type": "select",
            "table_name": table_name,
            "opt": 2,
            "option_field": option_field,
            "option_value": option_value,
            "fields": fields
        }

        res = db_sock.db_sock(data)
        if res:
            print(f'success: {res} {type(res)}')
            json_data = json.loads(res)
            ret = json_data[1][field_key]
            return float(ret)
        else:
            return None

    except Exception as e:
        print(f'error: {e}')
        return e


### 2024-01-17 OK
### 사용법 : GET_QUAN_COIN(symbol)
### 출력값 : 000.0 (Type : float)
### 에러시 : exception
def GET_QUAN_COIN(symbol):
    table_name = "sim_wallet"
    option_field = "name"
    option_value = symbol
    field_key = "cur_balance_coin"
    fields = ["name", field_key, "time"]

    try:
        data = {
            "query_type": "select",
            "table_name": table_name,
            "opt": 2,
            "option_field": option_field,
            "option_value": option_value,
            "fields": fields
        }

        res = db_sock.db_sock(data)
        if res:
            print(f'success: {res} {type(res)}')
            json_data = json.loads(res)
            ret = json_data[1][field_key]
            return float(ret)
        else:
            return None

    except Exception as e:
        print(f'error: {e}')
        return e

### 2024-01-17 OK
### 사용법 : GET_CASH()
### 출력값 : 000.0 (Type : float)
### 에러시 : exception
def GET_CASH():
    table_name = "sim_cash"
    option_field = ""
    option_value = ""
    field_key = "cur_balance_cash"
    fields = [field_key, "time"]

    try:
        data = {
            "query_type": "select",
            "table_name": table_name,
            "opt": 0,
            "option_field": option_field,
            "option_value": option_value,
            "fields": fields
        }

        res = db_sock.db_sock(data)
        if res:
            print(f'success: {res} {type(res)}')
            json_data = json.loads(res)
            ret = json_data[0]['cur_balance_cash']
            return float(ret)
        else:
            return None

    except Exception as e:
        print(f'error: {e}')
        return e

### 2024-01-17 OK
### 사용법 : GET_CUR_PRICE(symbol, idx)
### 출력값 : 000.0 (Type : float)
### 에러시 : exception
def GET_CUR_PRICE(symbol, idx):
    symbols = {'KRW-XRP': 'ripple', 'KRW-BTC': 'bitcoin', 'KRW=ETH': 'ethereum'}
    if symbol not in symbols:
        print(f'error: Check the symbol name')
        return None

    table_name = symbols.get(symbol)
    option_field = "id"
    option_value = idx
    fields = ["name", "price", "trend", "time"]  # 조회하려는 필드 이름 목록

    try:
        data = {
            "query_type": "select",
            "table_name": table_name,
            "opt": 1,
            "option_field": option_field,
            "option_value": option_value,
            "fields": fields
        }

        res = db_sock.db_sock(data)
        if res:
            print(f'success: {res} {type(res)}')
            json_data = json.loads(res)
            ret = json_data[1]['price']
            return float(ret)
        else:
            return None

    except Exception as e:
        print(f'error: {e}')
        return e

# def db_sock.db_sock(data):
#     # 서버 설정
#     server_address = "15.164.217.243"  # 서버의 실제 IP 주소 또는 도메인 이름
#     server_port = 50086  # 서버 포트 번호

#     # 서버에 연결
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client_socket.connect((server_address, server_port))

#     try:
#         # 데이터를 JSON 형식으로 직렬화
#         request_json = json.dumps(data)

#         # 서버에 요청 보내기
#         client_socket.send(request_json.encode("utf-8"))

#         # 서버로부터 응답 받기
#         response_json = client_socket.recv(1024).decode("utf-8")

#         return response_json

#     except Exception as e:
#         print(f'error: {e}')
#         return None

#     finally:
#         # 클라이언트 소켓 닫기
#         client_socket.close()

if __name__ == '__main__':
    # print("sim_pyupbit.py")

    ### GET_CUR_PRICE 사용
    coin = 'KRW-XRP'
    idx = 7465
    while idx < 7467:
        ret = GET_CUR_PRICE(coin, idx)
        print(f'DG {ret} {type(ret)}')
        idx += 1
        time.sleep(1)
    print('END')

    ### GET_CASH 사용
    ret = GET_CASH()
    print(f"DG {ret} {type(ret)}")

    ret = GET_QUAN_COIN(coin)
    print(f"DG {ret} {type(ret)}")

    ret = GET_BUY_AVG(coin)
    print(f"DG {ret} {type(ret)}")

    coin = 'KRW-XRP'
    ret = GET_ORDER_STATE(coin)
    print(f"DG {ret} {type(ret)}")

    ret = GET_ORDER_INFO(3)
    print(f"DG {ret} {type(ret)}")

    

