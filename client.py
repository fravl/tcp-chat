import socket 
import threading
import os
import argparse

help = "@<name>: write to another user or group with name <name>\n" \
    "group <name> create: create a group with name <name>\n" \
    "group <name> delete: delete group\n" \
    "group <name> add <user>: add one or more users to group. separate users by spaces.\n" \
    "group <name> remove <user>: remove one or more users from group. separate users by spaces.\n" \
    "group <name> rename <name>: rename a group\n" \
    "exit: close the chat client\n" \

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

print("Welcome to the chat client. After entering your nickname, write help to see available commands.")
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
        if(message == "help"):            
            print(help)
            continue
        if(message == "exit"):
            s.close()
            break
        s.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()