import time
import random
from db_parser import Database
from logs import Logs
from cache import Cache

def pop_end_dot(string):
    """
    Esta função remove o "." do fim da string ou devolve a string inalterada no caso de não existir "." no fim da string.

    Autor: Pedro Martins

    :param string: String
    :return: String
    """
    if string[-1] == ".":
        return string[:-1]
    return string

def init_send_query(flags, q_name, q_type):
    """
    Esta função recebe os dados necessários para criar uma query.
    Com esses dados é criada uma string com o formato correto para ser enviada ao servidor e ser respondida.

    Autor: Pedro Martins

    :param flags: String
    :param q_name: String
    :param q_type: String
    :return: String
    """
    ids = set(range(1, 65535))
    id = random.choice(tuple(ids))
    string = f"{id},{flags},0,0,0,0;{q_name},{q_type};"
    return string

# Passou a estar inutilizada.
def respond_query(query, s, address, confs, log, cache):
    """
    Esta função recebe uma query e envia uma resposta a essa mesma query.
    A função recebe o socket e o endereço para o qual deverá enviar a resposta o que permite a esta função ser executada por uma thread de forma independente ao servidor.
    A função também recebe o ficheiro de configuração para saber se o dominio descrito na query é um dominio para o qual o servidor opera.
    Os ficheiros de logs também são atualizados dependendo da do que aconteça na resposta da query.
    A resposta à query é depois procurada na cache.

    Autor: Miguel Pinto e Pedro Martins

    :param query: String
    :param s: Socket
    :param address: Tuple (endereço, porta)
    :param confs: Configs
    :param log: Logs
    :param cache: Cache
    :return: Void
    """
    t_start = time.time()
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    arr = query.split(";")

    # Header
    header = arr[0]
    h_fields = header.split(",")
    if len(h_fields) != 6:
        # Sintaxe desconhecida da seguinte mensagem no header.
        log.er(time.time(), address, dados=query)
        return
    message_id = h_fields[0]
    flags = h_fields[1]
    #response_code = h_fields[2]
    #num_responses = h_fields[3]
    #num_authorities = h_fields[4]
    #num_extra = h_fields[5]

    # Data: Query Info
    data_qi = arr[1]
    qi_fields = data_qi.split(",")
    if len(qi_fields) != 2:
        # Sintaxe desconhecida da seguinte mensagem no campo Query Info.
        log.er(time.time(), address, dados=query)
        return
    q_name = qi_fields[0]
    q_type = qi_fields[1]

    # Indica nos logs, a receção de uma query relativa a um determinado domínio.
    log.qr(t_start, address, query, domain=q_name)

    if len(arr) < 3:
        log.er(time.time(), address, dados=query, domain=q_name)
        result = f"{message_id},,3,0,0,0;{q_name},{q_type};"  # sendo 3 o código de mensagem não descodificada.
        s.sendto(result.encode("utf-8"), address)
        return

    '''
    # Pelo menos por enquanto esta parte é desnecessaria uma vez que faço isto para queries de perguntas, sem esperar nenhum valor de resposta.
    # Terceira parte da mensagem onde vem informaçao de resposta
    # Data: List of Response, Authorities and Extra Values
    response_qi = arr[2]
    if response_qi:
        resp_fields = response_qi.split(",")
        responses = []
        for r in resp_fields:
            responses.append(r)    
    '''

    # Verifica se deve responder a queries sobre o dominio mencioando, relativo aos DD's.
    respondable_domains = confs.get_all_dd()
    if respondable_domains and q_name not in respondable_domains:
        # A query é ignorada se o servidor não for responsável pelo domínio mencionado na query.
        log.ev(time.time(), f"Foi ignorada a seguinte query, uma vez que este servidor não é responsável pelo domínio da query: {query}")
        return

    # Procura em cache, retornando já a string a enviar.
    result = cache.get_answers(log, message_id, q_name, q_type)

    # Envio da mensagem para o respetivo endereço
    s.sendto(result.encode("utf-8"), address)
    log.rp(time.time(), address, result, domain=q_name)

