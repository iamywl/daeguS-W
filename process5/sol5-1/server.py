import socket
import threading
import datetime

def handle_client(client_socket, addr):
    print(f'클라이언트와 연결됨. ({addr[0]}:{addr[1]})')
    client_socket.sendall('클라이언트와 연결됨.'.encode('utf-8'))

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print(f'클라이언트 연결 끊김: {addr[0]}:{addr[1]}')
                break
            message = data.decode('utf-8')
            print(f'클라이언트 수신: {message}')

            if message.lower() == 'quit':
                print(f'클라이언트 요청으로 연결 끊김: {addr[0]}:{addr[1]}')
                break

            response = message
            if '안녕' in message:
                response = '안녕! 뭐 물어볼래?'
            elif '이름' in message:
                response = '나는 에코 서버.'
            elif '시간' in message:
                response = f'현재 시간: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

            client_socket.sendall(response.encode('utf-8'))
        except ConnectionResetError:
            print(f'클라이언트 연결 강제 종료: {addr[0]}:{addr[1]}')
            break
        except Exception as e:
            print(f'오류 발생: {e}')
            break
    client_socket.close()

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('소켓 생성완료')

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print(f'호스트 이름: {host_name}')
    print(f'호스트 IP: {host_ip}')

    port = 9999
    server_address = (host_ip, port)

    try:
        server_socket.bind(server_address)
    except Exception as e:
        print(f'소켓 바인딩 오류: {e}')
        server_socket.close()
        return

    server_socket.listen(3)
    print(f'서버 대기 중... {server_address[0]}:{server_address[1]}')

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
        except KeyboardInterrupt:
            print('서버 종료.')
            break
        except Exception as e:
            print(f'클라이언트 연결 수락 중 오류 발생: {e}')
            break

    server_socket.close()

if __name__ == '__main__':
    run_server()