import socket 
import threading
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    'protocol', 
    metavar='P', 
    type=str, 
    nargs='?',
    choices=['ipv4','ipv6'], 
    default='ipv6',
    help="choose ipv4 or ipv6 protocol for the client"
)

args = parser.parse_args()
if(args.protocol == 'ipv4'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
else:
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) 

host = socket.gethostname() # Get server host name
port = 8080 
os.system('cls' if os.name == 'nt' else 'clear') # clear console
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