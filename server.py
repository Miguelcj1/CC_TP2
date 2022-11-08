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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(sp)

    s.send(dom.encode("utf-8")) # envia o dominio

    msg = s.recv(1024) # espera receber o nº de entradas da base de dados
    msg.decode("utf-8")

    #verifica se pode receber aquilo tudo (não percebo bem qual será o criterio para isto)

    s.send(msg.encode("utf-8")) #envia o nº de entradas que quer receber

    # deve receber todas as entradas de base de dados em um determinado tempo


def primaryServer(dom, port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", port)) # Recebe conexoes de todos (nao aplica restriçoes)
    s.listen()
    while True:
        conn, addr = s.accept() # rececão de uma conexão.
        with conn:
            print(f"Connected by {addr}")
            msg = conn.recv(1024)
            #msg.decode("utf-8")
            if addr not in dom.get_ss():
                # significa que não é um servidor secundário válido
                print(f"O endereço {addr} não corresponde a nenhum endereço de SS conhecido pelo SP do domínio {dom}!!")
                conn.close()
            elif msg != dom.get_name():
                # O nome do domínio, não é o dominio deste SP
                print(f"O nome do domínio recebido: {msg}, não é o dominio deste SP: {dom}!!")
                conn.close()
            else:
                # envia o nº de entradas das bases de dados
                n_lines = 2 #####
                n_lines = str(n_lines)
                s.send(n_lines)
                msg = s.recv(1024)  # nº de entradas que o SS quer receber
                if msg == n_lines:
                    # deve enviar todas as entradas do ficheiro de base de dados numerados sem comentarios
                    pass
                else:
                    # O SS não aceitou o nº de linhas para enviar.
                    pass


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
        databases[name] = db # adiciona o ponto final, para coerencia na busca de informaçao para queries.

    '''
    ### TESTE ###
    # constroi uma string no formato da mensagem que vai ser transmitida.
    #cache = Cache()
    id = 12
    q = query.init_send_query(id, "Q+A", "example.com.", "MX")
    res = query.respond_query(q, confs, databases, cache, log)

    ### FIM ###
    '''

    # Inicia os pedidos de transferencia de zona dos que são servidores secundários.
    for sp in sp_domains:
        pass

    endereco = '127.0.0.1'
    porta = 3334


    # Abertura do socket UDP.
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