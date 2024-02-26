import socket

def 

def db_sock():
    # 서버 설정
    server_address = "43.201.69.120"  # 서버의 실제 IP 주소 또는 도메인 이름
    server_port = 51316         # 서버 포트 번호

    # 요청할 테이블과 필드 설정
    table_name = "sim_wallet"
    fields = "name&&price&&time"  # 조회하려는 필드 이름 목록

    # 서버에 연결
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))

    # 서버에 요청 보내기
    request = f"{table_name},{fields}"
    client_socket.send(request.encode("utf-8"))

    # 서버로부터 응답 받기
    response = client_socket.recv(1024).decode("utf-8")

    # 응답 출력
    print(f"{table_name} {fields}")
    print(response)

    # 클라이언트 소켓 닫기
    client_socket.close()
    return response

