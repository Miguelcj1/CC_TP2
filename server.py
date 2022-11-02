import socket
import time
from config_parser import Configs
from logs import Logs
from db_parser import Database
import query



def main(conf):

    ttl = 20000
    mode = "debug"
    # Guarda a altura em que o servidor arrancou.
    ts_arranque = time.time()

    # Obtenção de um objeto que vai conter toda a informação proveniente do config_file.
    try:
        confs = Configs(conf)
    except Exception as exc:
        print(str(exc))
        print("Inicialização do servidor interrompida!")
        return

    # Obtenção de um objeto que tem informação sobre a escrita nos ficheiros de log e stdout.
    log = Logs(confs, mode)

    # Obtençao de um objeto database para cada dominio (que tenha uma database) com a informação sobre o dominio.
    databases = {}
    for name in confs.get_domain_names():
        try:
            db = Database(confs.get_db_path(name))
        except Exception as exc:
            #print (str(exc))
            log.fl(time.time(), str(exc), name)
            log.sp(time.time(), str(exc))
            return
        databases[name] = db

    ### TESTE ###
    # constroi uma string no formato da mensagem que vai ser transmitida.
    q = query.init_send_query(12, "Q+A", "example.com.", "MX")
    query.respond_query(q, databases)

    ### FIM ###

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