#!/usr/bin/env python3
import socket, json, threading, sys, os
from pathlib import Path

class Client:
    def __init__(self, user):
        self.user = user
        self.sock = socket.create_connection(('65.75.201.11', 12345))
        self.sock.sendall(json.dumps({'user': user}).encode())
        self.db = Path(f"msgs_{user}.json")
        self.msgs = json.loads(self.db.read_text()) if self.db.exists() else []
        threading.Thread(target=self._listen, daemon=True).start()
        print(f"✓ Connecté en tant que @{user} → 65.75.201.11:12345")
        print("→ Format: destinataire message\n   Ex: bob Salut !\n   Ex: * Bonjour à tous\n   /q pour quitter\n")

    def _listen(self):
        buf = ""
        while True:
            try:
                buf += self.sock.recv(1024).decode()
                while '\n' in buf:
                    line, buf = buf.split('\n', 1)
                    if line.strip():
                        m = json.loads(line)
                        if m.get('to') in (self.user, '*'):
                            print(f"\n📨 @{m['from']}: {m['text']}")
                            self.msgs.append({'dir': 'in', 'from': m['from'], 'text': m['text']})
                            self._save()
                            print(f"\n{self.user}> ", end='', flush=True)
            except: break
        print("\n\n⚠ Déconnecté"); sys.exit(0)

    def _save(self):
        self.db.write_text(json.dumps(self.msgs, ensure_ascii=False))

    def run(self):
        while True:
            try:
                line = input(f"{self.user}> ").strip()
                if line == '/q': break
                if not line or ' ' not in line: continue
                to, text = line.split(' ', 1)
                msg = {'to': to, 'text': text}
                self.sock.sendall((json.dumps(msg) + '\n').encode())
                self.msgs.append({'dir': 'out', 'to': to, 'text': text})
                self._save()
            except (EOFError, KeyboardInterrupt): break
        self.sock.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <votre_pseudo>")
        sys.exit(1)
    Client(sys.argv[1]).run()