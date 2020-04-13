'''
ftp服务器
'''

from socket import *
import os,sys,time,signal

FILE_PATH = "/home/tao/ftpFile/"
HOST = '0.0.0.0'
PORT = 8000
ADDR = (HOST,PORT)

class FtpServer(object):
	def __init__(self,c):
		self.c = c

	def do_list(self):
		file_list = os.listdir(FILE_PATH)
		if not file_list:
			self.c.send("文件库为空".encode())
		else:
			self.c.send(b'OK')
			time.sleep(0.1)
		
		files = ''
		for file in file_list:
			if file[0] != '.' and os.path.isfile(FILE_PATH + file):
				files = files+file+'#'
		self.c.sendall(files.encode())

	def do_get(self,filename):
		try:
			fd = open(FILE_PATH + filename,'rb')
		except:
			self.c.send('文件不存在'.encode())
			return
		self.c.send(b'OK')
		time.sleep(0.1)

		while True:
			data = fd.read(1024)
			if not data:
				time.sleep(0.1)
				self.c.send(b'##')
				break
			self.c.send(data)
		print("文件发送完毕")

	def do_put(self,filename):
		try:
			fd = open(FILE_PATH + filename,'wb')
		except:
			self.c.send('上传失败')
			return
		self.c.send(b'OK')

		while True:
			data = self.c.recv(1024)
			if data == b'##':
				break
			fd.write(data)
		fd.close()
		print("获得上传文件：",filename)




def main():
	sockfd = socket()
	sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	sockfd.bind(ADDR)
	sockfd.listen(5)

	signal.signal(signal.SIGCHLD,signal.SIG_IGN)
	print("Listen to the port 8000...")

	while True:
		try:
			c,addr = sockfd.accept()
		except KeyboardInterrupt:
			sockfd.close()
			sys.exit("服务器退出")
		except Exception as e:
			print('Error',e)
			continue

		print("已连接客户端：",addr)
		pid = os.fork()
		if pid == 0:
			sockfd.close()
			ftp = FtpServer(c)
			while True:
				data = c.recv(1024).decode()
				if not data or data[0] == 'Q':
					c.close()
					sys.exit("客户端退出")
				elif data[0] == 'L':
					ftp.do_list()
				elif data[0] == 'G':
					filename = data.split(' ')[-1]
					ftp.do_get(filename)
				elif data[0] == 'P':
					filename = data.split(' ')[-1]
					ftp.do_put(filename)

		else:
			c.close()
			continue


if __name__ == '__main__':
	main()