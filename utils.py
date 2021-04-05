import pickle, uuid, os, time
from model import Message
from tkinter import filedialog

clients = []
nicknames = []

# encaminha as mensagens serializadas para os clientes conectados, exceto ao remetente
def broadcast(message, current_client):
    for client in clients:
        if current_client != client:
            send_serialized(client, message)


# encaminha as mensagens da lógica de arquivo para os clientes conectados, exceto ao remetente
def broadcastFile(message, current_client):
    for client in clients:
        if current_client != client:
            client.send(message)


# serializa a mensagem e as envia atravez do dado cliente
def send_serialized(client, message, the_type='text'):
    obj_to_send = Message()
    obj_to_send.message = message
    obj_to_send.type = the_type
    client.send(pickle.dumps(obj_to_send))


# retorna com o objeto desserializado 
def get_serialized_message(client, data=None):
    if data is None:
        obj = pickle.loads(client.recv(1024))
        return obj
    return pickle.loads(data)


# faz o logout do cliente (desconect, remove dos dics, etc..)
def logout(client):
    index = clients.index(client)
    nickname = nicknames[index]
    broadcast(f'{nickname} saiu.', client)
    clients.remove(client)
    client.close()
    nicknames.remove(nickname)

# envia o arquivo do cliente remetente para o servidor
def send_file_to_server(client, nickname, mode):
    if mode == 'cmd':
        file_path = input('Informe o arquivo [*Apenas jpg, png, gif e txt]: ')
    elif mode == 'gui':
        file_path = filedialog.askopenfilename(initialdir = "/",title = "Escolha um arquivo",filetypes = (("jpeg files","*.jpg"),("png files","*.png*"),("gif files","*.gif"),("txt files","*.txt")))
    
    if file_path.lower().endswith(('.png', '.jpg', '.gif', '.txt')):

        extension = get_file_extension(file_path)
    
        try:
            arq = open(file_path,'rb')
            send_serialized(client, f'{nickname} enviou o arquivo: {file_path}')
            time.sleep(.01)

            client.send(extension.encode('utf-8'))
            time.sleep(.01)

            data = arq.read()
            client.send(data)
            time.sleep(.01)

            client.send('DONE'.encode('utf-8'))
            arq.close()
        except:
            print('Arquivo não encontrado.')
            time.sleep(.01)
            client.send('ERROR'.encode('utf-8'))
            time.sleep(.01)
            client.send('DONE'.encode('utf-8'))

    else:
        print('Arquivo inválido.')


# servidor recebe arquivo do cliente remetente e encaminha para os demais clientes
def server_resend_file(client, message):
    unique_filename = str(uuid.uuid4())
    while message:
        if (message == b"DONE" or message == b"ERROR"):
            broadcastFile(message, client)
            message = client.recv(1024)
        else:
            broadcastFile(message, client)
            message = client.recv(1024)


# recebe e salva o arquivo encaminhado pelo sevidor
def client_receive_save_file(client, message):
    unique_filename = str(uuid.uuid4())

    if (message == b"ERROR"):
        message = client.recv(1024)
    else:
        extension = get_file_extension(message, 'binary')
        filename = f'_{unique_filename}{extension}'
        arq = open(filename,'wb')
        cont = 0
        while message:
            cont = cont + 1
            if cont > 1:
                if (message == b"DONE"):
                    print(f'Arquivo salvo como: {filename}')
                    arq.close()
                    break
                else:
                    arq.write(message)
                    message = client.recv(1024)
            else:
                message = client.recv(1024)
        arq.close()


# retorna a extensão do arquivo 
def get_file_extension(entry_data, entry_type='filename'):

    if entry_type == 'filename':
        if entry_data.lower().endswith(('.png')):
            return '.png'
        if entry_data.lower().endswith(('.gif')):
            return '.gif'
        if entry_data.lower().endswith(('.jpg')):
            return '.jpg'
        
    elif entry_type == 'binary':
        if entry_data == b".jpg":
            return '.jpg'
        if entry_data == b".gif":
            return '.gif'
        if entry_data == b".png":
            return '.png'

    return '.txt'
