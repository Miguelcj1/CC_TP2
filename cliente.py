import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# endereco = socket.gethostname() # '10.0.0.10'

endereco = '127.0.0.1'
porta = 3333 # porta qualquer acima de 1024

msg = "Adoro Redes :)"

s.sendto(msg.encode('utf-8'), (endereco, porta))