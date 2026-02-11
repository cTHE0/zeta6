#!/usr/bin/env python3
import socket, threading, json

print("✓ serveur actif sur 65.75.201.11:12345")
clients = {}
sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 12345))
sock.listen()

def handle_client(conn, addr):
    user = json.loads(conn.recv(99).decode())['user']
    clients[conn] = user
    print(f"+ @{user}")
    while True:
        try:
            msg = json.loads(conn.recv(999).decode())
            msg['from'] = user
            for c in clients:
                if c != conn:
                    c.sendall((json.dumps(msg) + '\n').encode())
        except:
            break
    print(f"- @{clients.pop(conn, '?')}")
    conn.close()

while True:
    threading.Thread(target=handle_client, args=sock.accept(), daemon=True).start()