import socket
import threading
import sys, os

print("Python version:", sys.version)
print("Working directory:", os.getcwd())

# Connection Data
host = '127.0.0.1'
port = 55555
ENCODING = 'ascii'

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []

# Sending Messages To All Connected Clients
def broadcast(message, is_binary=False):
    for client in clients:
        if is_binary:
            client.send(message)
        else:
            client.send(message.encode(ENCODING))

# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            if message.startswith(b'PHOTO'):
                broadcast(message, is_binary=True)
            else:
                msg = message.decode(ENCODING)
                if msg.startswith('KICK'):
                    if nicknames[clients.index(client)] == 'admin':
                        name_to_kick = msg[5:]
                        kick_user(name_to_kick)
                    else:
                        client.send('Command was refused!'.encode(ENCODING))
                elif msg.startswith('BAN'):
                    if nicknames[clients.index(client)] == 'admin':
                        name_to_ban = msg[4:]
                        kick_user(name_to_ban)
                        with open('bans.txt', 'a') as f:
                            f.write(f'{name_to_ban}\n')
                        print(f'{name_to_ban} was banned!')
                    else:
                        client.send('Command was refused!'.encode(ENCODING))
                else:
                    broadcast(message.decode(ENCODING))

        except socket.error:
            if client in clients:
                index = clients.index(client)
                # Index is used to remove client from list after getting disconnected
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left the Chat!')
                nicknames.remove(nickname)
                break

# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        # Request And Store Nickname
        client.send('NICK'.encode(ENCODING))

        nickname = client.recv(1024).decode(ENCODING)

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if nickname+'\n' in bans:
            client.send('BAN'.encode(ENCODING))
            client.close()
            continue

        if nickname == 'admin':
            client.send('PASS'.encode(ENCODING))
            password = client.recv(1024).decode(ENCODING)

            if password != 'admin':
                client.send('REFUSE'.encode(ENCODING))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat!')
        client.send('Connected to server!'.encode(ENCODING))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You Were Kicked from Chat !'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked from the server!'.encode('ascii'))

print("Server is listening...")
receive()