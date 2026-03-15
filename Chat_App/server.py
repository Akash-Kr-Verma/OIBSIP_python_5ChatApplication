import socket
import threading

# Connection Data
HOST = '127.0.0.1'  # Localhost
PORT = 55555        # Valid ports are 0-65535, keep >1024 to avoid system ports

# Lists to keep track of connected users
clients = []
nicknames = []

# Start Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

def broadcast(message):
    """Sends a message to all connected clients."""
    for client in clients:
        try:
            client.send(message)
        except:
            # If sending fails, remove the client
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left!'.encode('ascii'))
            nicknames.remove(nickname)

def handle(client):
    """Handles individual client connections."""
    while True:
        try:
            # Receive message from client
            message = client.recv(1024)
            broadcast(message)
        except:
            # If client disconnects
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left!'.encode('ascii'))
                nicknames.remove(nickname)
                break

def receive():
    """Main loop to accept new connections."""
    print(f"Server is running on {HOST}:{PORT}...")
    while True:
        # Accept connection
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # Request Nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        
        # Store data
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname is {nickname}")
        broadcast(f"{nickname} joined!".encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))

        # Start a thread for this client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive()