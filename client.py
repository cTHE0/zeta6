import socket,json,threading,sys,os
u=sys.argv[1];f=f"m_{u}.json";h=json.loads(open(f).read())if os.path.exists(f)else[]
s=socket.create_connection(('65.75.201.11',12345));s.sendall((json.dumps({'u':u})+'\n').encode())
def r():
 b=''
 while 1:
  b+=s.recv(999).decode()
  while'\n'in b:l,b=b.split('\n',1);m=json.loads(l);print(f"\n📩 @{m['f']}: {m['t']}");h.append(m);open(f,'w').write(json.dumps(h))
threading.Thread(target=r,daemon=1).start()
while 1:
 l=input(f"{u}> ").strip()
 if l=='/q':break
 t=l.split(' ',1);d=t[0]if len(t)>1else'*';m={'to':d,'t':t[1]if len(t)>1else t[0]};s.sendall((json.dumps(m)+'\n').encode());h.append({'f':u,'to':d,'t':m['t']});open(f,'w').write(json.dumps(h))
s.close()