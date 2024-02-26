import socket
import json

host = '43.201.69.120'
port = 56303
print(f"{type(host)} {type(port)}")
def start_client(server_host=host, server_port=port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, server_port))

        # JSON 데이터 전송
        data_to_send = {"type": "greeting", "content": "Hello, server!"}
        s.sendall(json.dumps(data_to_send).encode())

        # 서버로부터 응답 수신
        data = s.recv(1024)
        print(f"Received response: {data.decode()}")

if __name__ == "__main__":
    start_client()


