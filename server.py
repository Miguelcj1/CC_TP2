import socket
from config_parser import Configs

def main(conf):

    # Obtenção de um objeto que vai conter toda a informação proveniente do config_file.
    confs = Configs(conf)

    if confs.is_sp():
        print("Sou o servidor principal!")
    else:
        print("Sou um servidor secundário do servidor principal" + confs.get_sp() + "!")

    # Abertura do socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    endereco = ''
    porta = 3333
    s.bind((endereco, porta))

    print(f"Estou à escuta no {endereco}:{porta}")

    while True:
        msg, add = s.recvfrom(1024)
        print(msg.decode('utf-8'))
        print(f"Recebi uma mensagem do cliente {add}")


    s.close()

if __name__ == '__main__':
    main("configuração")