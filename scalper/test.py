import uuid

t_uuid = uuid.uuid4()
data = {
    't_uuid':t_uuid,
    'name':'test'
}
print(data['t_uuid'])


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