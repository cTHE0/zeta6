#!/usr/bin/env python3
import socket, threading, json, sys

PORT = 12345
clients = {}  # {socket: username}

def relay(conn, addr):
    try:
        # Premier message = identifiant utilisateur
        user = json.loads(conn.recv(256).decode())['user'][:32]  # limite 32 caractères
        clients[conn] = user
        print(f"+ {addr[0]} → @{user}")
        
        while True:
            data = conn.recv(1024)
            if not data: break
            msg = json.loads(data.decode())
            msg['from'] = user
            # Relais à tous les clients sauf l'expéditeur
            for c, u in clients.items():
                if c != conn:
                    try: c.sendall((json.dumps(msg) + '\n').encode())
                    except: pass
    except: pass
    finally:
        print(f"- {addr[0]} ← @{clients.pop(conn, '?')}")
        conn.close()

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PORT))
    s.listen()
    print(f"✓ Relais actif sur 65.75.201.11:{PORT} (ouvert à tous)")
    print("  → Aucun stockage côté serveur — messages sauvegardés localement par les clients\n")
    while True:
        threading.Thread(target=relay, args=s.accept(), daemon=True).start()

if __name__ == '__main__':
    main()