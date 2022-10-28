import socket
import time
from config_parser import Configs
from logs import Logs

def main(conf):

    ttl = 20000
    mode = "debug"
    # Guarda a altura em que o servidor arrancou-
    ts_arranque = time.time()

    # Obtenção de um objeto que vai conter toda a informação proveniente do config_file.
    confs = Configs(conf)
    if confs is None:
        print("Inicialização do servidor interrompida!")
        return

    # Obtenção de um objeto que tem informação sobre a escrita de logs.
    log = Logs(confs)

    endereco = ''
    porta = 3334

    # Reportar no log o arranque do servidor.
    log.st(ts_arranque, porta, ttl, mode)

    # Abertura do socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((endereco, porta))

    print(f"Estou à escuta no {endereco}:{porta}")
    print("----------------------")

    while True:
        msg, add = s.recvfrom(1024)
        msg = msg.decode('utf-8')
        print(msg)
        log.qr(time.time(), add, msg) # escrita do evento QR no log
        print(f"Recebi uma mensagem do cliente {add}")
        print("----------------------")


    s.close()

if __name__ == '__main__':
    main("configuração")