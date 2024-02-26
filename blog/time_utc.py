import datetime

def utc_to_timestamp(utc_time_str):
    try:
        utc_datetime = datetime.datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")
        timestamp = int(utc_datetime.timestamp())
        return timestamp
    except ValueError:
        return None

def convert_utc_to_kst(utc_timestamp):
    try:
        datetime_utc = datetime.datetime.utcfromtimestamp(utc_timestamp)
        datetime_utc = datetime.datetime.fromtimestamp(timestamp=utc_timestamp)
        datetime_seoul = datetime_utc + datetime.timedelta(hours=9)
        return datetime_utc, datetime_seoul
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None, None

# 타임스탬프 또는 날짜를 입력 받아서 UTC와 KST로 변환
input_value = input("타임스탬프 또는 날짜 입력 (예: '1615159613' 또는 '2021-03-07 23:26:53'): ")

try:
    # 입력값이 숫자로 이루어져 있으면 타임스탬프로 가정
    if input_value.isdigit():
        timestamp = int(input_value)
    else:
        # 입력값이 날짜 형식이면 타임스탬프로 변환
        timestamp = utc_to_timestamp(input_value)

    datetime_utc, datetime_seoul = convert_utc_to_kst(timestamp)
except ValueError:
    print("올바른 입력 형식이 아닙니다.")
    datetime_utc, datetime_seoul = None, None

if datetime_utc is not None and datetime_seoul is not None:
    print(f"UTC 타임스탬프 값: {int(datetime_utc.timestamp())}")
    print(f"KST 타임스탬프 값: {int(datetime_seoul.timestamp())}")
