import socket

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    server_address = (host_ip, 9999)

    print(f'서버 연결 시도 중... {server_address[0]}:{server_address[1]}')
    try:
        client_socket.connect(server_address)
        print('서버 연결됨.')

        initial_message = client_socket.recv(1024).decode('utf-8')
        print(f'서버 응답: {initial_message}')

        while True:
            message_to_send = input('메시지 입력 (종료: quit): ')
            if not message_to_send:
                continue

            client_socket.sendall(message_to_send.encode('utf-8'))

            if message_to_send.lower() == 'quit':
                print('연결 종료.')
                break

            data = client_socket.recv(1024)
            if not data:
                print('서버 연결 끊김.')
                break

            received_message = data.decode('utf-8')
            print(f'서버 Echo: {received_message}')

    except ConnectionRefusedError:
        print('서버 실행 안 됨.')
    except Exception as e:
        print(f'클라이언트 오류 발생: {e}')
    finally:
        client_socket.close()

if __name__ == '__main__':
    run_client()