ELEC-C7420 Basic Principles in Networking Spring 2023
# Assignment 2: Command Line TCP Chat 

This project implements some basic functionalities of a command line messaging application using Python TCP sockets.
To run the application locally install the requirements using `pip install -r requirements.txt`, then run server.py to start the server.
Now, to add clients to the chat run client.py in a different command prompt for each client and begin chatting.

## Features
- Messaging
  - User can send a message to another user or a group
- Group management
  - Users can create groups
  - Owner can delete, rename, and add or remove users from a group
- Offline messages
  - Users see messages they received while offline upon going online
- Sender notification
  - Sender gets a notified whether recipient recieved message or was offline

## Limitations
- Application state is only saved in-memory
- No password protection
- No GUI
