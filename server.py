#!/usr/bin/env python3
import socket, threading, json

PORT = 12345
clients = {}  # {socket: username}

def handle(conn, addr):
    try:
        # Lecture identifiant (JSON + \n)
        buf = b''
        while b'\n' not in buf:
            buf += conn.recv(256)
        user = json.loads(buf.split(b'\n')[0].decode())['user'][:32]
        clients[conn] = user
        print(f"✅ @{user} connecté depuis {addr[0]}")
        
        # Boucle de relais
        buf = b''
        while True:
            data = conn.recv(1024)
            if not data: break
            buf += data
            while b'\n' in buf:
                line, buf = buf.split(b'\n', 1)
                if line.strip():
                    msg = json.loads(line.decode())
                    msg['from'] = user
                    for c in list(clients.keys()):
                        if c != conn:
                            try: c.sendall((json.dumps(msg) + '\n').encode())
                            except: 
                                print(f"❌ @{clients.pop(c, '?')} déconnecté (envoi échoué)")
                                c.close()
    except: pass
    finally:
        print(f"👋 @{clients.pop(conn, '?')} déconnecté")
        conn.close()

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PORT))
    s.listen()
    print(f"📡 Relais actif sur 65.75.201.11:{PORT}")
    print("   → Zéro stockage serveur | Messages sauvegardés localement\n")
    while True:
        threading.Thread(target=handle, args=s.accept(), daemon=True).start()

if __name__ == '__main__':
    main()