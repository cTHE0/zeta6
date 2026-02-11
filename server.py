import socket, threading, json
print("✓ serveur actif 65.75.201.11:12345");c={};s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('',12345));s.listen()
def h(x,a):
 u=json.loads(x.recv(99).decode())['u'];c[x]=u;print(f"+ @{u}")
 while 1:
  try:
   m=json.loads(x.recv(999).decode());m['f']=u
   for y in c:
    if y!=x:y.sendall((json.dumps(m)+'\n').encode())
  except:break
 print(f"- @{c.pop(x,'?')}");x.close()
while 1:threading.Thread(target=h,args=s.accept(),daemon=1).start()