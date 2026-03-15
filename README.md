# OIBSIP_python_5ChatApplication


A **multi-client chat server** built using **Python socket programming and threading**.  
The server allows multiple users to connect, send messages, and communicate with each other in real time.

This project demonstrates **network programming, concurrent connections, and message broadcasting using TCP sockets**.

---

## Features

- Real-time **multi-client communication**
- **TCP socket-based server**
- Supports **multiple users simultaneously**
- **Nickname system** for user identification
- Automatic **join and leave notifications**
- **Thread-based client handling**
- Simple and lightweight implementation

---

## Project Structure

```
chat-server
│
├── server.py      # Main chat server implementation
└── README.md      # Project documentation
```

---

## Technologies Used

- **Python**
- **Socket Programming**
- **Threading**
- **TCP Networking**

---

## How the Chat Server Works

1. The server starts and listens on a specific **host and port**.

2. When a client connects:
   - The server requests a **nickname**.
   - The nickname is stored in a list.

3. Each client connection runs in a **separate thread**, allowing multiple users to chat simultaneously.

4. When a user sends a message:
   - The server **broadcasts the message** to all connected clients.

5. If a user disconnects:
   - The server removes them from the client list.
   - Other users receive a **leave notification**.

---

## Installation

### 1. Clone the repository



### 2. Navigate to the project folder

```
cd chat-server
```

---

## Running the Server

Run the following command:

```
python server.py
```

If successful, you will see:

```
Server is running on 127.0.0.1:55555...
```

---

## Example Workflow

1. Start the server
2. Multiple clients connect
3. Each user enters a nickname
4. Messages are broadcast to all connected users

Example chat:

```
Alice joined!
Bob joined!

Alice: Hello everyone!
Bob: Hi Alice!
```

---

## Key Concepts Demonstrated

- **TCP socket communication**
- **Client-server architecture**
- **Multithreading**
- **Real-time message broadcasting**
- **Network programming fundamentals**

---
