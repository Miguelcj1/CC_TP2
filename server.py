import socket
import time
import sys
import traceback
import threading
import auxs
from cache import Cache
from config_parser import Configs
from logs import Logs
from db_parser import Database
import query
from cache import Cache

# addr = (endereço, porta)
# lstradd = ["endereço:porta" ou "endereco"]
def check_addr(addr, lstradd):
    for s in lstradd:
        arr = s.split(":")
        if arr[0] == addr[0]:
            if len(arr) == 2:
                if arr[1] == addr[1]:
                    return True
                else:
                    return False
            else:
                return True
    return False

# Utilizada por um SS para pedir pelas entradas de base de dados de um domínio.
def ask_zone_transfer(log, confs, cache, dom):
    # Guarda a timestamp do início do processo.
    t_start = time.time()

    # Obtém o (endereço, porta) do servidor principal do dominio "dom".
    addr = confs.get_sp(dom)

    # Cria o socket TCP.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.bind(('', port)) ### TEST
    s.settimeout(100) # aplica um tempo em que tem de acabar a transferencia de zona.

    # Tenta conectar-se ao endereço do servidor principal especificado no tuplo adress_port.
    s.connect(addr)

    # Envia o nome do dominio cuja base de dados requisita como maneira de iniciar o pedido.
    s.send(dom.encode("utf-8"))

    try:
        msg = s.recv(1024) # Espera receber o nº de entradas da base de dados que vão ser enviadas.
        lines_to_receive = int(msg.decode("utf-8"))
        lines_received = 0
        s.send(msg) # reenvia o nº de linhas como maneira de indicar que quer que se começe a transferencia.

        buf = ""
        msg = "1"
        flag = True
        while flag:
            if msg:
                msg = s.recv(1024) # mensagem vem na forma (i;dados)
                msg = msg.decode("utf-8")
                buf += msg
            buf_f = buf.split("\n", 1)
            single_line = buf_f[0]
            if len(buf_f) > 1:
                buf = buf_f[1]
            arr = single_line.split(";")
            n_line = int(arr[0]) # talvez adicionar verificação de ordem ((not sure))
            data = arr[1]
            cache.update_with_line(log, data, "SP")
            if n_line >= lines_to_receive:
                flag = False

        t_end = time.time()
    except socket.timeout:
        print("Ocorreu um timeout!") # Fazer algo quando ocorre um timeout.
        log.ez(time.time(), str(addr), "SS", dom)


# Utilizada por um SP para responder a pedidos de transferência de zona.
def resp_zone_transfer(log, confs, dbs, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", port)) # Recebe conexoes de todos (nao aplica restriçoes)
    s.listen()
    while True:
        conn, addr = s.accept() # rececão de uma conexão.
        t_start = time.time()
        with conn:
            msg = conn.recv(1024)
            msg = msg.decode("utf-8")
            if msg not in confs.get_sp_domains():
                # O nome do domínio, não é um dominio principal neste servidor.
                conn.send("erro".encode("utf-8"))
                # chamar algum metodo de log
                print(f"O nome do domínio recebido: {msg}, não é conhecido pelo servidor!!")
                conn.close()
                break
            dom = msg
            ss_addresses_l = confs.get_ss(dom) # ["endereço" ou "endereço:porta"]
            if not check_addr(addr, ss_addresses_l): # significa que este endereço não é um endereço de um SS conhecido, negando a conexao.
                conn.send("Erro".encode("utf-8"))
                log.ez(time.time(), str(addr), "SP", dom)
                conn.close()
                break
            else:
                # envia o nº de entradas das bases de dados
                db = dbs.get(dom) # isto nunca deve retornar null uma vez que é feita uma verificação similar atras.
                entry_lines = db.all_db_lines()
                n_lines = len(entry_lines)
                n_lines = str(n_lines)
                conn.send(n_lines.encode("utf-8"))
                msg = conn.recv(1024)  # nº de entradas que o SS quer receber
                msg = msg.decode("utf-8")
                if msg == n_lines: # Envia todas as entradas do ficheiro de base de dados numerados sem comentarios
                    i = 1
                    for l in entry_lines:
                        msg = f"{i};{l}\n"
                        i += 1
                        conn.send(msg.encode('utf-8'))
                    ## receçao de alguma mensagem de confirmaçao.
                    t_end = time.time()
                    duracao = t_end - t_start
                else:
                    # O SS não aceitou o nº de linhas para enviar.
                    log.ez(time.time(), str(addr), "SP", dom)
                    conn.close()
                    break
    s.close()

# * -> significa opcional
def main(): # argumentos: nome_do_script  ficheiro_configuraçao  porta*  timeout*  modo="DEBUG"*

    # Guarda a altura em que o servidor arrancou.
    ts_arranque = time.time()

    if len(sys.argv) < 2: # nº de argumentos obrigatorios
        print("Não foram passados argumentos suficientes.")

    # Path do ficheiro de configuração do servidor.
    conf = sys.argv[1]

    porta = 5000 ### 53
    timeout = 200
    mode = "DEBUG"
    if len(sys.argv) > 2:
        porta = int(sys.argv[2])
        timeout = int(sys.argv[3])
        mode = sys.argv[4]

    endereco = ''

    # Obtenção de um objeto que vai conter toda a informação proveniente do config_file.
    try:
        confs = Configs(conf)
    except Exception as exc:
        print(str(exc))
        print("Inicialização do servidor interrompida devido a falha no ficheiro de configuração!")
        return

    sp_domains = confs.get_sp_domains()
    ss_domains = confs.get_ss_domains()

    # Obtenção de um objeto que tem informação sobre a escrita nos ficheiros de log e stdout.
    log = Logs(confs, mode)

    # Reportar no log o arranque do servidor.
    log.st(ts_arranque, porta, timeout, mode)

    # Inicializa a cache com valores nulos.
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
        databases[name] = db


    # Inicia os pedidos de transferencia de zona dos que são servidores secundários.
    if sp_domains:
        # Abre uma thread para que possa atender a transferencias de zona.
        threading.Thread(target=resp_zone_transfer, args=(log, confs, databases, porta)).start()
        ###resp_zone_transfer(log, confs, databases, porta)

    # Para cada dominio secundário, pede ao respetivo servidor principal a sua base de dados.
    for ss in ss_domains:
        ask_zone_transfer(log, confs, cache, ss)


    # Abertura do socket UDP.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((endereco, porta))

    print(f"Estou à escuta no {endereco}:{porta}")
    print("--------------------------------")


    while True:
        msg, address = s.recvfrom(1024)
        msg = msg.decode('utf-8')
        log.qr(time.time(), address, msg) # escrita do evento QR no log
        answer = query.respond_query(msg, confs, databases, cache, log)

        s.sendto(answer.encode('utf-8'), address)


    s.close()

if __name__ == '__main__':
    main()