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
    Data da última atualização: 18/11/2022
"""

def check_addr(addr, lstradd):
    """
    Esta função verifica se o endereço addr faz parte da lista de endereços recebida lstradd, verificando o ip e a porta.

    Autor: Pedro Martins.

    :param addr: Tuple (endereço, porta)
    :param lstradd: list(String) ["endereço:porta" ou "endereco"]
    :return: Boolean
    """
    for single in lstradd:
        arr = single.split(":")
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
    Exemplo: '10; TTL DEFAULT 86400' , retorna 10.

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


def ask_zone_transfer(dom, soarefresh=-1):
    """
    Esta função faz a parte do SS na transferencia de zona estabelecendo uma conexão TCP com o SP do dominio recebido.
    A informação recebida é guardada na cache, e os ficheiros de logs são atualizados com o que acontece neste processo.
    O argumento 'soarefresh' é utilizado para a chamada recursiva de si próprio, ou seja, quando o ask_zone_transfer terminar com sucesso, será aberta outra thread que correrá esta função mas com um intervalo de SOAREFRESH.

    Autor: Miguel Pinto e Pedro Martins.

    :param dom: String (nome do domínio)
    :param soarefresh: Float (intervalo de espera após ser chamada a função)
    :return: Void
    """

    my_serialnumber = -1
    # Para que haja uma verificação de atualização da base de dados, é passada esta variavel.
    if soarefresh > 0:
        time.sleep(soarefresh)
        my_serialnumber = cache.get_soa(dom, "SOASERIAL")

    # Guarda a timestamp do início do processo.
    t_start = time.time()

    # Obtém o (endereço, porta) do servidor principal do dominio "dom".
    addr = confs.get_sp(dom)

    # Cria o socket TCP.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)  # tempo que um recv chamada neste socket, esperará.

    # Tenta conectar-se ao endereço do servidor principal especificado em addr.
    s.connect(addr)

    # Requisita o serial number da base de dados ao mandar "{dom}, SOASERIAL".
    req = f"{dom},SOASERIAL"
    s.send(req.encode("utf-8"))
    try:
        msg = s.recv(1024)  # Espera receber o serial number da base de dados.
        if msg.decode("utf-8") == "DENIED": # Significa que não foi dada permissão pelo SP o acesso à base de dados.
            log.ez(time.time(), addr, "SS foi negado o acesso.", dom)
            return
        db_serialnumber = int(msg.decode("utf-8"))
        # Significa que a versão atual da base de dados do SS ainda não precisa de atualização.
        if db_serialnumber == my_serialnumber:
            s.send("NOZT".encode("utf-8"))
            s.close()
            soarefresh = cache.get_soarefresh(dom)
            threading.Thread(target=ask_zone_transfer, args=(dom, soarefresh)).start()
            return
        cache.free_domain(dom)

        # Envia o nome do dominio cuja base de dados requisita como maneira de iniciar o pedido.
        s.send(dom.encode("utf-8"))

        msg = s.recv(1024)  # Espera receber o nº de entradas da base de dados que vão ser enviadas.

        lines_to_receive = int(msg.decode("utf-8"))
        s.send(msg)  # reenvia o nº de linhas como maneira de indicar que quer que se começe a transferencia.

        buf = ""  # 'buf' vai conter uma string com todas as linhas enviadas, separadas por \n
        while True:
            msg = s.recv(1024)  # mensagem vem na forma (i;dados)
            msg = msg.decode("utf-8")
            buf += msg
            if is_final_msg(msg, lines_to_receive):
                break

        s.close()

        lines = buf.split("\n")  # 'lines' é um array das linhas enviadas pelo SP.
        lines = sorted(lines, key=get_line_number)  # Ordena as linhas recebidas caso tenham vindo desordenadas.
        n_line = -1

        for single_line in lines:
            arr = single_line.split(";")
            try:
                n_line = int(arr[0])
            except ValueError:
                log.ez(time.time(), addr, "SS", dom)
                return
            data = arr[1]
            cache.update_with_line(log, data, "SP")

        t_end = time.time()
        duracao = (t_end - t_start) * 1000
        log.zt(time.time(), addr, "SS", duracao=duracao, domain=dom)

        # Começo o processo de SOAREFRESH para fazer refresh aos seus dados.
        soarefresh = cache.get_soarefresh(dom)
        threading.Thread(target=ask_zone_transfer, args=(dom, soarefresh)).start()

    except socket.timeout:
        s.close()
        log.to(time.time(), addr, f"Timeout por parte do SS no pedido de transferência de zona, sobre o domínio {dom}.", domain=dom)
        log.ez(time.time(), addr, "SS", dom)


def resp_zone_transfer(dbs, port):
    """
    Esta função faz a parte do SP na transferencia de zona recebendo conexões de SS.
    O SP so responderá a SS autorizados e apenas responde a transferencias sobre o dominio ao qual é SP.
    Os ficheiros de logs são atualizados com o que acontece neste processo.

    Autor: Miguel Pinto e Pedro Martins.

    :param dbs: Database
    :param port: Int
    :return: Void
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", port))
    s.listen()

    try:
        while True:
            conn, addr = s.accept() # rececão de uma conexão.
            t_start = time.time()
            with conn:
                msg = conn.recv(1024) # espera receber um soaserial request
                msg = msg.decode("utf-8")
                arr = msg.split(",")
                dom = arr[0]
                ss_addresses_l = confs.get_ss(dom)  # ["endereço" ou "endereço:porta"]
                if dom not in confs.get_sp_domains() or not check_addr(addr, ss_addresses_l):
                    # O nome do domínio, não é um dominio principal neste servidor.
                    conn.send("DENIED".encode("utf-8"))
                    log.ez(time.time(), addr, "SP negou o acesso.", dom)
                    continue
                serial_number = str(cache.get_soa(dom, "SOASERIAL"))
                conn.send(serial_number.encode("utf-8")) # envia o seu serial number.

                msg = conn.recv(1024) # espera receber o nome do domínio.
                msg = msg.decode("utf-8")
                if msg == "NOZT":
                    continue # o outro servidor não necessita da transferência.

                # envia o nº de entradas das bases de dados
                db = dbs.get(dom)
                entry_lines = db.all_db_lines()
                numb_lines = len(entry_lines)
                n_lines = str(numb_lines)
                conn.send(n_lines.encode("utf-8"))
                msg = conn.recv(1024)  # nº de entradas que o SS quer receber
                msg = msg.decode("utf-8")
                # Se o número recebido for o mesmo que o enviado, todas as entradas do ficheiro de base de dados numerados sem comentarios.
                if msg != n_lines:
                    # O SS não aceitou o nº de linhas para enviar.
                    log.ez(time.time(), addr, "SP", dom)
                    continue
                i = 1
                for l in entry_lines:
                    msg = f"{i};{l}"
                    if i != numb_lines:
                        msg += "\n"
                    conn.send(msg.encode('utf-8'))
                    i += 1

                t_end = time.time()
                duracao = t_end - t_start
                duracao *= 1000 # Passa duração para milisegundos.
                log.zt(time.time(), addr, "SP", duracao=duracao, domain=dom)
    except KeyboardInterrupt:
        print("fechei tpc")
        s.close()




"""
Esta função implementa o comportamento dos servidores principais/secundários no sistema DNS.
A função recebe um ficheiro de configuração como argumento onde obtém toda a informação que necessita.
Cada servidor irá possuir um objeto Logs e Cache onde poderá atualizar os ficheiros de log e guardar as informações necessarias em cache, respetivamente.

Dependendo do ficheiro de configuração o servidor poderá ser SP ou SS:
    Se for SP o servidor lança uma thread que executa a função resp_zone_transfer e fica à escuta de pedidos de transferencia de zona.
    Se for SS o servidor inicia um pedido de transferencia de zona ao SP do seu dominio.

Depois de concluídos os respetivos processos de transferências de zona, o servidor abre um socket UDP e espera a receção de queries de clientes.
Ao receber uma query lança uma thread para responder a essa query e volta a ficar a escuta de mais queries.

Autor: Miguel Pinto e Pedro Martins.

argument conf : String (config_file path)
argument porta : Int (Optional) 5000
argument timeout : Int (Optional) 10
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
timeout = 10
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
    #print("Inicialização do servidor interrompida devido a falha no ficheiro de configuração!")
    sys.exit("Ocorreu um erro na leitura do ficheiro de configuração!")

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
        db1 = Database(confs.get_db_path(name), cache, "FILE", log)
    except Exception as exc:
        log.fl(time.time(), str(exc), name)
        log.sp(time.time(), str(exc))
        traceback.print_exc()
        sys.exit("Ocorreu um erro no parsing da base de dados!")
    databases[name] = db1


# Inicia o atendimento a pedidos de transferencia de zona de servidores secundários.
if sp_domains:
    # Abre uma thread para que possa atender a transferencias de zona.
    threading.Thread(target=resp_zone_transfer, args=(databases, porta)).start()

# Para cada dominio secundário, pede ao respetivo servidor principal a sua base de dados.
for ss in ss_domains:
    ask_zone_transfer(ss)

# Abertura do socket UDP.
endereco = ''
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((endereco, porta))

try:
    while True:
        msg0, address = s.recvfrom(1024)
        msg0 = msg0.decode('utf-8')
        # Irá criar uma nova thread para atender a query recebida.
        query.respond_query(msg0, s, address, confs, log, cache)
except KeyboardInterrupt:
    print("fechei udp")
    s.close()

