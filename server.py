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

"""
Server.py:
    Módulo de implementação dos servidores do sistema DNS.
    Data de criação: 27/10/2022
    Data da última atualização: 13/11/2022
"""

def check_addr(addr, lstradd):
    """
    Esta função verifica se o endereço addr faz parte da lista de endereços recebida lstradd, verificando o ip e a porta.

    Autor: Pedro Martins.

    :param addr: Tuple (endereço, porta)
    :param lstradd: list(String) ["endereço:porta" ou "endereco"]
    :return: Boolean
    """
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

def get_line_number(string):
    """
    Esta função recebe uma linha da base de dados numerada e devolve o número dessa linha.
    Exemplo: 10;TTL DEFAULT 86400 , retorna 10.

    Autor: Miguel Pinto.

    :param string: String
    :return: Int
    """
    #lambda l: int(l.split(";")[0])
    inteiro = int(string.split(";")[0])
    return inteiro

def is_final_msg(string, last_i):
    """
    Esta função verifica se o número da string é o mesmo do que last_i.

    Autor: Miguel Pinto.

    :param string: String
    :param last_i: Int
    :return: Boolean
    """
    split_msg = string.split("\n")
    if split_msg[-1]:
        last_line = split_msg[-1]
        num = get_line_number(last_line)
        return num == last_i
    else:
        return False


def ask_zone_transfer(log, confs, cache, dom, timeout):
    """
    Esta função faz a parte do SS na transferencia de zona estabelecendo uma conexão TCP com o SP do dominio recebido.
    A informação recebida é guardada na cache, e os ficheiros de logs são atualizados com o que acontece neste processo.

    Autor: Miguel Pinto e Pedro Martins.

    :param log: Logs
    :param confs: Configs
    :param cache: Cache
    :param dom: String
    :param timeout: Int
    :return: Void
    """
    # Guarda a timestamp do início do processo.
    t_start = time.time()

    # Obtém o (endereço, porta) do servidor principal do dominio "dom".
    addr = confs.get_sp(dom)

    # Cria o socket TCP.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #port = 5001
    #s.bind(('', port)) ### Especificaria a porta usada para envio.
    s.settimeout(timeout)  # tempo que um recv chamada neste socket, esperará.

    # Tenta conectar-se ao endereço do servidor principal especificado no tuplo adress_port.
    s.connect(addr)

    # Envia o nome do dominio cuja base de dados requisita como maneira de iniciar o pedido.
    s.send(dom.encode("utf-8"))

    try:
        msg = s.recv(1024)  # Espera receber o nº de entradas da base de dados que vão ser enviadas.

        ### TALVEZ SIMPLESMENTE N DEVA ESPERAR QUE RETORNA ERRO DESISTINDO ATRAVES DO TIMEOUT
        if msg.decode("utf-8") == "erro": # Significa que não foi dada permissão pelo SP o acesso à base de dados.
            log.ez(time.time(), str(addr), "SP", dom)
            return

        lines_to_receive = int(msg.decode("utf-8"))
        s.send(msg)  # reenvia o nº de linhas como maneira de indicar que quer que se começe a transferencia.

        buf = ""  # 'buf' vai conter uma string com todas as linhas enviadas, separadas por \n
        while True:
            msg = s.recv(1024)  # mensagem vem na forma (i;dados)
            msg = msg.decode("utf-8")
            buf += msg
            if is_final_msg(msg, lines_to_receive):
                break

        lines = buf.split("\n")  # 'lines' é um array das linhas enviadas pelo SP.
        lines = sorted(lines, key=get_line_number)  # Ordena as linhas recebidas caso tenham vindo desordenadas.

        for single_line in lines:
            arr = single_line.split(";")
            # n_line = int(arr[0])
            data = arr[1]
            cache.update_with_line(log, data, "SP")

        # ENVIA CONFIRMAÇAO PARA O SP do término da zona de transferência bem sucedido.
        s.send("1".encode("utf-8"))

        s.close()
        t_end = time.time()
        duracao = t_end - t_start
        duracao *= 1000
        log.zt(time.time(), addr, "SS", duracao=duracao, domain=dom)
    except socket.timeout:
        s.close()
        print("Ocorreu um timeout!")  # Fazer algo quando ocorre um timeout.
        log.ez(time.time(), str(addr), "SS", dom)


def resp_zone_transfer(log, confs, dbs, port):
    """
    Esta função faz a parte do SP na transferencia de zona recebendo conexões de SS.
    O SP so responderá a SS autorizados e apenas responde a transferencias sobre o dominio ao qual é SP.
    Os ficheiros de logs são atualizados com o que acontece nestes processo.

    Autor: Miguel Pinto e Pedro Martins.

    :param log: Logs
    :param confs: Confs
    :param dbs: Database
    :param port: Int
    :return: Void
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", port))  # Recebe conexoes de todos (nao aplica restriçoes)
    s.listen()
    while True:
        conn, addr = s.accept() # rececão de uma conexão.
        t_start = time.time()
        with conn:
            msg = conn.recv(1024)
            msg = msg.decode("utf-8")
            if msg not in confs.get_sp_domains():
                # O nome do domínio, não é um dominio principal neste servidor.
                conn.send("erro".encode("utf-8")) ### TALVEZ SIMPLESMENTE N DEVA RESPONDER DE VOLTA
                log.ez(time.time(), str(addr), "SP", dom)
                continue
            dom = msg
            ss_addresses_l = confs.get_ss(dom) # ["endereço" ou "endereço:porta"]
            if not check_addr(addr, ss_addresses_l): # significa que este endereço não é um endereço de um SS conhecido, negando a conexao.
                conn.send("erro".encode("utf-8")) ### TALVEZ SIMPLESMENTE N DEVA RESPONDER DE VOLTA
                log.ez(time.time(), str(addr), "SP", dom)
                continue

            # envia o nº de entradas das bases de dados
            db = dbs.get(dom)  # isto nunca deve retornar null uma vez que é feita uma verificação similar atras.
            entry_lines = db.all_db_lines()
            numb_lines = len(entry_lines)
            n_lines = str(numb_lines)
            conn.send(n_lines.encode("utf-8"))
            msg = conn.recv(1024)  # nº de entradas que o SS quer receber
            msg = msg.decode("utf-8")
            # Se o número recebido for o mesmo que o enviado, todas as entradas do ficheiro de base de dados numerados sem comentarios.
            if msg != n_lines:
                # O SS não aceitou o nº de linhas para enviar.
                log.ez(time.time(), str(addr), "SP", dom)
                continue
            i = 1
            for l in entry_lines:
                msg = f"{i};{l}"
                if i != numb_lines:
                    msg += "\n"
                conn.send(msg.encode('utf-8'))
                i += 1
            ###print("Ha espera de confirmaçao [Debug]")
            #conn.settimeout(10) # Espera 10 segundos pela confirmacao.
            msg = conn.recv(1024) # Confirmação de conclusão da transferencia de zona pelo outro lado.
            ###print("Passei da confirmaçao [Debug]") ###
            if msg.decode("utf-8") != "1":
                log.ez(time.time(), str(addr), "SP", dom)
                continue

            t_end = time.time()
            duracao = t_end - t_start
            duracao *= 1000 ## PASSA DURACAO PARA MILISEGUNDOS.
            log.zt(time.time(), addr, "SP", duracao=duracao, domain=dom)

    s.close()

def main():
    """
    Esta função implementa o comportamento dos servidores no sistema DNS.
    A função recebe um ficheiro de configuração como argumento onde obtem toda a informação que necessita.
    Cada servidor irá possuir um objeto Logs e Cache onde poderá atualizar os ficheiros de log e guardar as informações necessarias em cache, respetivamente.

    Dependendo do ficheiro de configuração o servidor poderá ser SP ou SS:
        Se for SP o servidor lança uma thread que executa a função resp_zone_transfer e fica à escuta de pedidos de transferencia de zona.
        Se for SS o servidor inicia um pedido de transferencia de zona ao SP do seu dominio.

    Depois de concluídas os respetivos processos de transferências de zona o servidor abre um socket UDP e espera a receção de queries de clientes.
    Ao receber uma query lança uma thread para responder a essa query e volta a ficar a escuta de mais queries.

    Autor: Miguel Pinto e Pedro Martins.

    argument conf: String (config_file path)
    argument porta : Int (Optional) 5000
    argument timeout : Int (Optional) 20
    argument mode : String (Optional) "Debug"
    :return: void
    """
    # Guarda a altura em que o servidor arrancou.
    ts_arranque = time.time()

    if len(sys.argv) < 2:  # nº de argumentos obrigatorios
        print("Não foram passados argumentos suficientes.")

    # Path do ficheiro de configuração do servidor.
    conf = sys.argv[1]

    porta = 5000
    timeout = 20
    mode = "DEBUG"
    if len(sys.argv) > 2:
        porta = int(sys.argv[2])
        timeout = int(sys.argv[3])
        mode = sys.argv[4]

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
            db = Database(confs.get_db_path(name), cache, "FILE", log)
        except Exception as exc:
            log.fl(time.time(), str(exc), name)
            log.sp(time.time(), str(exc))
            traceback.print_exc()
            return
        databases[name] = db


    # Inicia o atendimento a pedidos de transferencia de zona de servidores secundários.
    if sp_domains:
        # Abre uma thread para que possa atender a transferencias de zona.
        threading.Thread(target=resp_zone_transfer, args=(log, confs, databases, porta)).start()

    # Para cada dominio secundário, pede ao respetivo servidor principal a sua base de dados.
    for ss in ss_domains:
        ask_zone_transfer(log, confs, cache, ss, timeout)


    # Abertura do socket UDP.
    endereco = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((endereco, porta))

    print(f"Estou à escuta no {endereco}:{porta}")
    print("--------------------------------")


    while True:
        msg, address = s.recvfrom(1024)
        msg = msg.decode('utf-8')
        ####  ESTOU A ESPERA DE SABER SE A MENSAGEM DE LOG TEM DE SER ESCRITO NO DOMINIO ESPECIFICO OU NAO. ####
        #log.qr(time.time(), address, msg) # Indica o recebimento de uma query no ficheiro de log.
        threading.Thread(target=query.respond_query, args=(msg, s, address, confs, log, cache)).start()

    s.close()

if __name__ == '__main__':
    main()