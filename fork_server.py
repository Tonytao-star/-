from socket import *
import os,sys
import signal

def client_handler(c):
	print("处理子进程的请求：",c.getpeername())
	try:
		while True:
			data = c.recv(1024)
			if not data:
				break
			print(data.decode())
			c.send('收到客户端请求'.encode())
	except (KeyboardInterrupt,SystemError):
		sys.exit("客户端退出")
	except Exception as e:
		print(e)
	c.close()
	sys.exit(0)

HOST = ""
PORT = 8888
ADDR = (HOST,PORT)

s = socket()
s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
s.bind(ADDR)
s.listen(5)

print("主进程%d等待客户端连接"%os.getpid())
signal.signal(signal.SIGCHLD,signal.SIG_IGN)
while True:
	try:
		c,addr = s.accept()
	except KeyboardInterrupt:
		sys.exit("服务器退出")
	except Exception as e:
		print("Erroe",e)
		continue

	pid = os.fork()
	if pid == 0:
		s.close()
		client_handler(c)

	else:
		c.close()
		continue
