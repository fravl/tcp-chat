import socket 
import threading
import os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
host = socket.gethostname() # Get server host name
port = 8080 
os.system('cls' if os.name == 'nt' else 'clear')
uid = input("Enter nickname: ")


s.connect((host, port)) # Connect to server

def receive():
    while True:
        try:
            message = s.recv(1024).decode('ascii')
            if message == 'NICK':
                s.send(uid.encode('ascii'))
            else:
                for line in message.splitlines():
                    print(line)
        except:
            s.close()
            break

def write():
    while True:
        message = input("")     
        if(message == "exit"):
            s.close()
            break
        s.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()