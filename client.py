#!/usr/bin/env python3
import socket, json, threading, sys, os

user = sys.argv[1]
db = f"msgs_{user}.json"
history = json.loads(open(db).read()) if os.path.exists(db) else []

sock = socket.create_connection(('65.75.201.11', 12345))
sock.sendall((json.dumps({'user': user}) + '\n').encode())
print(f"@{user} connecté")

def receive():
    buf = ''
    while True:
        buf += sock.recv(999).decode()
        while '\n' in buf:
            line, buf = buf.split('\n', 1)
            msg = json.loads(line)
            if msg.get('to') in (user, '*'):
                print(f"\n📩 @{msg['from']}: {msg['text']}")
                history.append(msg)
                open(db, 'w').write(json.dumps(history))

threading.Thread(target=receive, daemon=True).start()

while True:
    line = input(f"{user}> ").strip()
    if line == '/q':
        break
    parts = line.split(' ', 1)
    dest = parts[0] if len(parts) > 1 else '*'
    text = parts[1] if len(parts) > 1 else parts[0]
    msg = {'to': dest, 'text': text}
    sock.sendall((json.dumps(msg) + '\n').encode())
    history.append({'from': user, 'to': dest, 'text': text})
    open(db, 'w').write(json.dumps(history))

sock.close()