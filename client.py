#!/usr/bin/env python3
import socket, json, threading, sys
from pathlib import Path

class Client:
    def __init__(self, user):
        self.user = user
        self.sock = socket.create_connection(('65.75.201.11', 12345))
        # Envoi identifiant AVEC \n
        self.sock.sendall((json.dumps({'user': user}) + '\n').encode())
        self.db = Path(f"msgs_{user}.json")
        self.msgs = json.loads(self.db.read_text()) if self.db.exists() else []
        threading.Thread(target=self._recv, daemon=True).start()
        print(f"✨ Connecté en tant que @{user}")
        print("→ Format: destinataire message   (ex: bob Salut !)")
        print("   → '*' pour diffusion: * Bonjour")
        print("   → /q pour quitter\n")

    def _recv(self):
        buf = ""
        while True:
            try:
                data = self.sock.recv(1024).decode()
                if not data: break
                buf += data
                while '\n' in buf:
                    line, buf = buf.split('\n', 1)
                    if line.strip():
                        m = json.loads(line)
                        if m.get('to') in (self.user, '*'):
                            print(f"\n📩 @{m['from']}: {m['text']}")
                            self.msgs.append({'dir':'in','from':m['from'],'text':m['text']})
                            self._save()
                            print(f"\n{self.user}> ", end='', flush=True)
            except: break
        print("\n\n🔌 Déconnecté du serveur"); sys.exit(0)

    def _save(self):
        self.db.write_text(json.dumps(self.msgs, ensure_ascii=False, indent=2))

    def run(self):
        while True:
            try:
                line = input(f"{self.user}> ").strip()
                if line == '/q': break
                if not line: continue
                
                # Parsing intelligent : premier mot = destinataire, reste = message
                parts = line.split(' ', 1)
                to = parts[0] if len(parts) > 1 else '*'
                text = parts[1] if len(parts) > 1 else parts[0]
                
                # Envoi
                msg = {'to': to, 'text': text}
                self.sock.sendall((json.dumps(msg) + '\n').encode())
                self.msgs.append({'dir':'out','to':to,'text':text})
                self._save()
            except (EOFError, KeyboardInterrupt): break
        self.sock.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <votre_pseudo>")
        sys.exit(1)
    Client(sys.argv[1]).run()