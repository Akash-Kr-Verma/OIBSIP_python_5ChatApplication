import socket
import threading

# Choose a nickname
nickname = input("Choose your nickname: ")

# Connect to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

def receive():
    """Listens for incoming messages from Server."""
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    """Sends messages to Server."""
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode('ascii'))

# Run threads for listening and writing simultaneously
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()