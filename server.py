#!/usr/bin/env python3
import socket
import threading
import json

HOST, PORT = '0.0.0.0', 12345
clients = {}  # {client_socket: username}

def broadcast(sender, msg):
    for sock, user in clients.items():
        if sock != sender:
            try:
                sock.sendall(json.dumps(msg).encode() + b'\n')
            except:
                sock.close()
                del clients[sock]

def handle_client(conn, addr):
    print(f"[+] Connexion de {addr}")
    try:
        # Premier message = nom d'utilisateur
        data = conn.recv(1024).decode().strip()
        user = json.loads(data)['user']
        clients[conn] = user
        print(f"  → Utilisateur: {user}")

        while True:
            data = conn.recv(4096)
            if not data:
                break
            msg = json.loads(data.decode().strip())
            msg['from'] = user
            print(f"[MSG] {user} → {msg['to']}: {msg['text'][:50]}")
            broadcast(conn, msg)
    except Exception as e:
        print(f"[-] Erreur {addr}: {e}")
    finally:
        print(f"[-] Déconnexion de {clients.get(conn, addr)}")
        clients.pop(conn, None)
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"✓ Serveur relais démarré sur {HOST}:{PORT}")
        print("  → Aucun stockage côté serveur\n")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    main()