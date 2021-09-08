import threading
import socket
HOST = socket.gethostbyname(socket.gethostname())
PORT = 55555	

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)
    

def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)
            if msg.decode('ascii').startswith('KICK'):
                
                if nicknames[clients.index(client)] == 'admin':
                    nameToKick = msg.decode('ascii')[5:]
                    kickUser(nameToKick)
                else:
                    client.send('command was refused'.encode('ascii'))

            elif msg.decode('ascii').startswith('BAN'):

                if nicknames[clients.index(client)] == 'admin':
                    nameToBan = msg.decode('ascii')[4:]
                    kickUser(nameToBan)
                    
                    with open('bans.txt', 'a') as f:
                        f.write(f'{nameToBan}\n')

                    print(f'{nameToBan} was baned')
                
                else:
                    client.send('command was refused'.encode('ascii'))
            else:
                broadcast(message)
        
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left the chat'.encode('ascii'))
                nicknames.remove(nickname)
                break 


def receive():
    while True:
        client, address = server.accept()
        print(f"conneted with {str(address)}")
        client.send('NICK'.encode('ascii'))
        nickname =  client.recv(1024).decode('ascii')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()
        
        if nickname + '\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if nickname == 'admin':
            client.send("PASS".encode('ascii'))
            password = client.recv(1024).decode('ascii') 
            if password != "pass1234":
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)

        print(f"nickname : {nickname}")
        broadcast(f"{nickname} joined".encode('ascii'))
        client.send('Connected to the server'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


def kickUser(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        clientToKick = clients[name_index]
        clients.remove(clientToKick)
        clientToKick.send("You were kicked by an admin".encode('ascii'))
        clientToKick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by admin'.encode('ascii'))

        
print("server is listening ... ")
receive()