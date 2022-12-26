import time
import random
from db_parser import Database
from logs import Logs
from cache import Cache
import auxs
import socket

def belongs_to_domain(q_name, domains):
    for d in domains:
        if q_name.endswith(d):
            return True
    return False


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

def get_response_code(string):
    """
    Retorna o response code da query.
    :param string: String da query.
    :return: Inteiro que representa o response code da query.
    """
    arr = string.split(",")
    code = arr[2]
    return int(code)

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
    :param address: Tuple (endereço, porta) sendo o endereço destinatário da resposta.
    :param confs: Configs
    :param log: Logs
    :param cache: Cache
    :return: Void
    """
    t_start = time.time()
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    arr = query.split(";")

    ###################### PARSING DA QUERY ######################
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


    # Verifica se deve responder a queries sobre o dominio mencioando, relativo aos DD's.
    respondable_domains = confs.get_all_dd()
    if respondable_domains and not belongs_to_domain(q_name, respondable_domains):
        # A query é ignorada se o servidor não for responsável pelo domínio mencionado na query.
        log.ev(time.time(), f"Foi ignorada a seguinte query, uma vez que este servidor não é responsável pelo domínio da query: {query}")
        return

    # Procura em cache, retornando já a string a enviar.
    result = cache.get_answers(log, message_id, q_name, q_type)

    # Envio da mensagem para o respetivo endereço
    s.sendto(result.encode("utf-8"), address)
    log.rp(time.time(), address, result, domain=q_name)


def get_closest_adresses(q_response):
    """
    Dada uma query response, analisa e obtém uma lista de endereços mais proximos do objetivo para contactar.
    :param q_response: Query response
    :return: lista de endereços(tuplos) mais proximos do objetivo para contactar
    """
    tokens = q_response.split(";")
    head = tokens[0]
    header_fields = head.split(",")
    response_code = header_fields[2]
    n_authorities = header_fields[4]
    n_extras = header_fields[5]
    query_name = tokens[1].split(",")[0]
    authorities_field = tokens[3]
    list_of_authorities = authorities_field.split(",")
    if n_authorities == 0 or n_extras == 0:
        return []

    # Organização da informação num dicionario(domain->lista_ns) (parsing)
    domain_to_ns = {}
    for a in list_of_authorities:
        arrr = a.split(" ")
        domain = arrr[0]
        ns = arrr[2]
        if domain_to_ns.get(domain) is None:
            domain_to_ns[domain] = []
        domain_to_ns[domain].append(ns)

    # Determinar qual o dominio mais próximo do q_name
    closest_domain = ""
    for d in domain_to_ns.keys():
        if query_name.endswith(d) and len(d) > len(closest_domain):
            closest_domain = d

    # Nomes dos dominios mais proximos do q_name
    ns_values = domain_to_ns[closest_domain]
    list_extras = tokens[4].split(",")
    ret = []
    for name in ns_values:
        for e in list_extras:
            e_fields = e.split(" ")
            e_name = e_fields[0]
            e_adress = e_fields[2]
            if e_name == name:
                ret.append(e_adress)
                break
    ret = map(auxs.str_adress_to_tuple, ret)
    return list(ret)


def respond_query_sr(query, s, address, confs, log, cache):
    """
    :param query: String
    :param s: Socket
    :param address: Tuple (endereço, porta) sendo o endereço destinatário da resposta.
    :param confs: Configs
    :param log: Logs
    :param cache: Cache
    :return: Void
    """
    t_start = time.time()
    arr = query.split(";")

    ###################### PARSING DA QUERY ######################
    # Header -> 123,Q,0,0,0,0;
    header = arr[0]
    h_fields = header.split(",")
    if len(h_fields) != 6: # Sintaxe desconhecida da seguinte mensagem no header.
        log.er(time.time(), address, dados=query)
        return
    message_id = h_fields[0]
    flags = h_fields[1]
    #response_code = h_fields[2]
    #num_responses = h_fields[3]
    #num_authorities = h_fields[4]
    #num_extra = h_fields[5]

    # Data: Query Info -> ;example.com.,MX;
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

    ###################### VERIFICAÇÃO DA CACHE ######################

    result = cache.get_answers(log, message_id, q_name, q_type)

    # GUARDA INFO EM CACHE.
    cache.update_with_query_response(log, result)

    # Se foi encontrada resposta na cache, não precisa de fazer o resto das verificações e envia a resposta.
    if get_response_code(result) == 0: # significa que foi encontrada resposta na cache.
        # Envio da mensagem final para o respetivo endereço
        s.sendto(result.encode("utf-8"), address)
        log.rp(time.time(), address, result, domain=q_name)
        return

    ###################### PROCURA ALTERNATIVA PERGUNTANDO A OUTROS SERVIDORES ######################

    # Cria um novo socket para enviar perguntas e receber as suas respostas.
    newsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Verifica se tem algum endereço para o qual deva mandar diretamente a query.
    direct_domains = confs.get_dd(q_name)
    for dd in direct_domains:
        newsocket.sendto(query.encode("utf-8"), dd)
        log.qe(time.time(), dd, query, domain=q_name)
        result, serv_addr = newsocket.recvfrom(1024)
        result = result.decode("utf-8")
        log.rr(time.time(), serv_addr, result, domain=q_name)
        #print(f"--------------- [DEBUG] -> Resposta recebida pelo DD:\n{result}\n---------------")
        # GUARDA INFO EM CACHE.
        cache.update_with_query_response(log, result)
        if get_response_code(result) != 3:
            break


    # Ignora o envio de mensagem ao ST no caso de ja obter resposta por parte do DD.
    if get_response_code(result) != 0:
        lista_de_st = confs.get_st_adresses()
        for st in lista_de_st:
            newsocket.sendto(query.encode("utf-8"), st)
            log.qe(time.time(), st, query, domain=q_name)
            result, serv_addr = newsocket.recvfrom(1024)
            result = result.decode("utf-8")
            log.rr(time.time(), serv_addr, result, domain=q_name)
            # GUARDA INFO EM CACHE.
            cache.update_with_query_response(log, result)
            if get_response_code(result) != 3:
                break

        closest_adresses = get_closest_adresses(result)
        for addr in closest_adresses:
            newsocket.sendto(query.encode("utf-8"), addr)
            log.qe(time.time(), addr, query, domain=q_name)
            result, serv_addr = newsocket.recvfrom(1024)
            result = result.decode("utf-8")
            log.rr(time.time(), serv_addr, result, domain=q_name)
            # GUARDA INFO EM CACHE.
            cache.update_with_query_response(log, result)


        result = cache.get_answers(log, message_id, q_name, q_type)
        print(f"--------------- [DEBUG]:\n{result}\n---------------------------------------------------------------------------")


    ###################### FIM DA PROCURA ALTERNATIVA ######################

    # Envio da mensagem final para o respetivo endereço
    s.sendto(result.encode("utf-8"), address)
    log.rp(time.time(), address, result, domain=q_name)





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