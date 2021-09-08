import threading
import socket

stop_thread = False

nickname = input("Enter a nickname : ")
if nickname == 'admin':
    password = input("Enter password for admin :")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))


def receive():
    while True:

        global stop_thread
        if stop_thread:
            break
        
        try:
            message = client.recv(1024).decode('ascii')
            
            if message == "NICK":
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                
                if next_message == 'PASS':
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        print("Connection refused wrong password")
                        stop_thread = True
                
                elif next_message == 'BAN':
                    print("Connection refused, you are baned")
                    client.close()
                    stop_thread = True
            
            else:
                print(message)
        
        except :
            print("error occurred")
            client.close()
            break
            

def write():
    while True:
        
        if stop_thread:
            break
        
        message = f'{nickname}: {input("")}'
        
        if message[len(nickname) + 2:].startswith('/'):
            
            if nickname == 'admin':
                
                if message[len(nickname) + 2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname) + 2 + 6:]}'.encode('ascii'))
                
                elif message[len(nickname) + 2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname) + 2 + 5:]}'.encode('ascii'))
            
            else:
                print("commands can only be executed by the admin")
        
        else:
            client.send(message.encode('ascii'))






receiveThread = threading.Thread(target=receive)
receiveThread.start()

writeThread = threading.Thread(target=write)
writeThread.start()
