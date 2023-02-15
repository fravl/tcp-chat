import socket # Import socket module

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
host = socket.gethostname() # Get server host name
port = 8080 


s.connect((host, port)) # Connect to server
print(s.recv(1024).decode()) # Print message from server
s.close() # Close the socket when done