#!/usr/bin/env python3
import socket
import json
import threading
import sys
import os
from pathlib import Path

class MessengerClient:
    def __init__(self, host, port, user):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.user = user
        self.db = Path(f"messages_{user}.json")
        self.history = self._load_history()
        
        # Envoi du nom d'utilisateur
        self.sock.sendall(json.dumps({'user': user}).encode() + b'\n')
        print(f"✓ Connecté en tant que '{user}' → {host}:{port}")
        print("Commandes: /users (liste), /quit (déconnexion)\n")

    def _load_history(self):
        return json.loads(self.db.read_text()) if self.db.exists() else []

    def _save_history(self):
        self.db.write_text(json.dumps(self.history, indent=2, ensure_ascii=False))

    def send_msg(self, to, text):
        msg = {'to': to, 'text': text}
        self.sock.sendall(json.dumps(msg).encode() + b'\n')
        self.history.append({'dir': 'out', 'to': to, 'text': text})
        self._save_history()

    def recv_loop(self):
        buf = b''
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                buf += data
                while b'\n' in buf:
                    line, buf = buf.split(b'\n', 1)
                    msg = json.loads(line.decode())
                    if msg['to'] == self.user or msg['to'] == '*':
                        print(f"\n[📨 {msg['from']}] {msg['text']}")
                        self.history.append({'dir': 'in', 'from': msg['from'], 'text': msg['text']})
                        self._save_history()
                        print(f"\n{self.user}> ", end='', flush=True)
            except:
                break
        print("\n\n⚠ Déconnecté du serveur")
        sys.exit(0)

    def run(self):
        threading.Thread(target=self.recv_loop, daemon=True).start()
        while True:
            try:
                line = input(f"{self.user}> ").strip()
                if not line:
                    continue
                if line == '/quit':
                    break
                if line == '/users':
                    print(f"Utilisateurs connectés: {', '.join(set(m['from'] for m in self.history if 'from' in m)) or 'aucun'}")
                    continue
                if ':' not in line:
                    print("Format: destinataire:message")
                    continue
                to, text = line.split(':', 1)
                self.send_msg(to.strip(), text.strip())
            except (EOFError, KeyboardInterrupt):
                break
        self.sock.close()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <serveur> <port> <votre_nom>")
        sys.exit(1)
    MessengerClient(sys.argv[1], int(sys.argv[2]), sys.argv[3]).run()