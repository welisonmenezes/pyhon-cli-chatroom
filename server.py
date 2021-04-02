import threading, socket, pickle
from model import Message
from utils import send_serialized, get_serialized_message, server_resend_file, broadcast, clients, nicknames, logout


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 10000))
server.listen()


# lida com as mensagens recebidas do cliente ligado à essa thread
def handle(client):
    while True:
        try:
            data = client.recv(1024)
            if data:
                try:
                    # caso seja dados serializados (mensagens comuns)
                    data = get_serialized_message(client, data)
                    if data.message == 'EXIT':
                        logout(client)
                        break
                    broadcast(data.message, client)
                except:
                    # mensagem não serializada (lógica de compartilhamento de arquivos)
                    try:
                        server_resend_file(client, data)
                    except:
                        pass
            else:
                logout(client)
                break
        except:
            logout(client)
            break


# escutando para receber novas conexões
def receive():
    while True:
        client, address = server.accept()
        print(f'Conectado com {str(address)}')

        # requisita e salva um nickname (um login fake)
        send_serialized(client, 'NICK')
        data = get_serialized_message(client)
        nickname = data.message
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname do client é {nickname}')
        broadcast(f'{nickname} entrou.', client)
        send_serialized(client, 'Conectado ao servidor! [-h para ajuda]')

        threading.Thread(target=handle, args=(client,)).start()


print('Server is listening...')
receive()