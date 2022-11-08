import socket
import time
import traceback
import auxs
from cache import Cache
from config_parser import Configs
from logs import Logs
from db_parser import Database
import query


def secundaryServer(dom, sp):
    q = dom # nome do domínio, enviado para receber a cópia da base de dados.
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.connect(sp)

    ss.send(dom.encode("utf-8")) # envia o dominio

    msg = ss.recv(1024) # espera receber o nº de entradas da base de dados
    msg.decode("utf-8")

    #verifica se pode receber aquilo tudo (não percebo bem qual será o criterio para isto)

    ss.send(msg.encode("utf-8")) #envia o nº de entradas que quer receber

    # deve receber todas as entradas de base de dados em um determinado tempo


def primaryServer(dom, port):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.bind((socket.gethostname(), port))
    ss.listen()

    while True:
        clienteSocket, address = ss.accept()
        msg = ss.recv(1024)
        msg.decode("utf-8") # recebe o dominio e terá de verificar a validade e se aquele address tem permissao para o fazer

        if address in dom.get_ss() and msg == dom.get_name():
            ss.send()       # envia o nº de entradas das bases de dados

            msg = ss.recv(1024) # nº de entradas que o SS quer receber

            # deve enviar todas as entradas do ficheiro de base de dados numerados sem comentarios



def main(conf):

    ttl = 200
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

    sp_domains = confs.get_sp_domains()
    ss_domains = confs.get_ss_domains()

    # Obtenção de um objeto que tem informação sobre a escrita nos ficheiros de log e stdout.
    log = Logs(confs, mode)

    porta = 3334
    # Reportar no log o arranque do servidor.
    log.st(ts_arranque, porta, ttl, mode)

    cache = Cache()

    # Obtençao de um objeto database para cada dominio (que tenha uma database) com a informação sobre o dominio.
    databases = {}
    for name in sp_domains:
        try:
            db = Database(confs.get_db_path(name), cache, "SP", log)
        except Exception as exc:
            log.fl(time.time(), str(exc), name)
            log.sp(time.time(), str(exc))
            traceback.print_exc()
            return
        databases[auxs.add_end_dot(name)] = db # adiciona o ponto final, para coerencia na busca de informaçao para queries.

    '''
    ### TESTE ###
    # constroi uma string no formato da mensagem que vai ser transmitida.
    #cache = Cache()
    id = 12
    q = query.init_send_query(id, "Q+A", "example.com.", "MX")
    res = query.respond_query(q, confs, databases, cache, log)

    #cache.search(id, "example.com.", "MX")

    ### FIM ###
    '''

    # Inicia os pedidos de transferencia de zona dos que são servidores secundários.
    #tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for sp in sp_domains:
        pass

    endereco = '127.0.0.1'
    porta = 3334



    # Abertura do socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((endereco, porta))

    print(f"Estou à escuta no {endereco}:{porta}")
    print("--------------------------------")


    while True:
        msg, address = s.recvfrom(1024)
        msg = msg.decode('utf-8')
        log.qr(time.time(), address, msg) # escrita do evento QR no log
        #print(f"Recebi uma mensagem do cliente {add}")
        #print("----------------------")
        answer = query.respond_query(msg, confs, databases, cache, log)

        s.sendto(answer.encode('utf-8'), address)


    s.close()

if __name__ == '__main__':
    main("configuração")