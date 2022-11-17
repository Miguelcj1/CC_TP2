import time
import random
import socket
import auxs
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
    #s.bind() ### SE TIVER DE TER UMA PORTA ESPECIFICA.

    arr = query.split(";")

    # Header
    header = arr[0]
    h_fields = header.split(",")
    if len(h_fields) != 6:
        log.er(time.time(), address, dados=query)
        #raise Exception(f"Sintaxe desconhecida da seguinte mensagem no header field: {query}")
        return
    message_id = h_fields[0]
    flags = h_fields[1]
    response_code = h_fields[2]
    num_responses = h_fields[3]
    num_authorities = h_fields[4]
    num_extra = h_fields[5]


    # Data: Query Info
    data_qi = arr[1]
    qi_fields = data_qi.split(",")
    if len(qi_fields) != 2:
        log.er(time.time(), address, dados=query)
        #raise Exception(f"Sintaxe desconhecida da seguinte mensagem no Query Info field: {query}")
        return
    q_name = qi_fields[0]
    q_type = qi_fields[1]

    # Indica o recebimento de uma query no ficheiro de log.
    log.qr(t_start, address, query, domain=q_name)

    if len(arr) < 3:
        log.er(time.time(), address, dados=query, domain=q_name)
        result = f"{message_id},,3,0,0,0;{q_name},{q_type};"  # sendo 3 o código de mensagem não descodificada.
        s.sendto(result.encode("utf-8"), address)
        return

    #talvez esta parte seja desnecessaria uma vez que faço isto para queries de perguntas.
    # Terceira parte da mensagem onde vem informaçao de resposta
    # Data: List of Response, Authorities and Extra Values
    response_qi = arr[2]
    if response_qi:
        resp_fields = response_qi.split(",")
        responses = []
        for r in resp_fields:
            responses.append(r)

    # Verifica se deve responder a queries deste dominio, relativamente aos DD's. ### CONFIRMAR SE ESTA RESTRIÇÃO É VALIDA.
    respondable_domains = confs.get_all_dd()
    if q_name not in respondable_domains:
        # A resposta irá com o response_code = 2.
        result = f"{message_id},,2,0,0,0;{q_name},{q_type};;" ### IGNORAR A MENSAGEM.
        log.rp(time.time(), address, result, domain=q_name)
        s.sendto(result.encode("utf-8"), address)
        return

    # Procura em cache
    result = cache.get_answers(log, message_id, q_name, q_type)

    # Envio da mensagem para o respetivo endereço
    #time.sleep(11) ##
    log.rp(time.time(), address, result, domain=q_name)
    s.sendto(result.encode("utf-8"), address)


'''
    ### PARTE EM BAIXO TECNICAMENTE É INUTIL.
    # Procura e obtenção de respostas na base de dados.
    db = dbs.get(q_name)
    if db is None:
        # O VALOR NAO FOI ENCONTRADO NA BASE DE DADOS E PROSSEGUIR COM O RESPETIVO PROCEDIMENTO.
        # Não irá ser respondida a query.
        return f"{message_id},A,2,0,0,0;{q_name},{q_type};;"

    all_values = []
    responses_f = ""
    authorities_f = ""
    extras_f = ""
    data = ""
    n_resp = 0
    arr_resp = []
    n_authorities = 0
    arr_authorities = []
    n_extras = 0
    arr_extras = []
    flags = "A"

    # Identificação do tipo de query
    if q_type in ["SOASP", "SOAADMIN", "SOASERIAL", "SOAREFRESH", "SOARETRY", "SOAEXPIRE"]:
        # Obtencao de response_values
        v = db.get_SOA_(q_type, q_name)
        if v is None:
            responses_f = ""
        else:
            n_resp += 1
            value = v[0]
            ttl = str(v[1])
            responses_f = " ".join((q_name, q_type, value, ttl))

    elif q_type == "NS":
        # Obtencao de response_values
        valores = db.get_NS(q_name)
        # valores = lista de tuplos (string, int, int)
        for v in valores:
            n_resp += 1
            value = v[0]
            ttl = v[1]
            prio = v[2]
            string = q_name + " NS " + value + " " + str(ttl)
            if prio > -1: # Verifica se foi indicado alguma prioridade. Se tiver o valor -1 não foi atribuida.
                string += " " + str(v[2])
            all_values.append(v[0]) # adiciona os valores dos response values aos all values
            arr_resp.append(string)
        responses_f = ",".join(arr_resp)

    elif q_type == "A":
        # Obtencao de response_values
        valores = db.get_A(q_name)
        # valores = lista de tuplos (string, int, int)
        for v in valores:
            n_resp += 1
            value = v[0]
            ttl = v[1]
            prio = v[2]
            string = q_name + " A " + value + " " + str(ttl)
            if prio > -1: # Verifica se foi indicado alguma prioridade. Se tiver o valor -1 não foi atribuida.
                string += " " + str(v[2])
            all_values.append(v[0]) # adiciona os valores dos response values aos all values
            arr_resp.append(string)
        responses_f = ",".join(arr_resp)

    elif q_type == "CNAME":
        # Obtencao de response_values
        v = db.get_CNAME(q_name)
        # v = (string, int)
        if v is not None:
            n_resp += 1
            value = v[0]
            ttl = v[1]
            string = q_name + " CNAME " + value + " " + str(ttl)
            all_values.append(v[0]) # adiciona os valores dos response values aos all values
            arr_resp.append(string)
            responses_f = ",".join(arr_resp)

    elif q_type == "MX":
        # Obtencao de response_values
        valores = db.get_MX(q_name)
        # valores = lista de tuplos (string, int, int)
        for v in valores:
            n_resp += 1
            value = v[0]
            ttl = v[1]
            prio = v[2]
            string = q_name + " MX " + value + " " + str(ttl)
            if prio > -1: # Verifica se foi indicado alguma prioridade. Se tiver o valor -1 não foi atribuida.
                string += " " + str(v[2])
            all_values.append(v[0]) # adiciona os valores dos response values aos all values
            arr_resp.append(string)
        responses_f = ",".join(arr_resp)

    elif q_type == "PTR":
        # Obtencao de response_values
        valores = db.get_PTR(q_name)
        # valores = lista de tuplos (string, int)
        for v in valores:
            n_resp += 1
            value = v[0]
            ttl = v[1]
            string = q_name + " PTR " + value + " " + str(ttl)
            all_values.append(v[0]) # adiciona os valores dos response values aos all values
            arr_resp.append(string)
        responses_f = ",".join(arr_resp)


    # Obtencao de authority_values
    authorities = db.get_NS(q_name)
    for a in authorities:
        n_authorities += 1
        value = a[0]
        ttl = a[1]
        prio = a[2]
        string = q_name + " NS " + value + " " + str(ttl)
        if prio > -1: # Verifica se foi indicado alguma prioridade. Se tiver o valor -1 não foi atribuida.
            string += " " + str(prio)
        all_values.append(a[0]) # adiciona os valores dos response values aos all values
        arr_authorities.append(string)
    authorities_f = ",".join(arr_authorities)

    # Obtencao de extra_values
    for v in all_values:
        extras = db.get_A(v)
        for e in extras:
            n_extras += 1
            value = e[0]
            ttl = e[1]
            prio = e[2]
            string = v + " A " + value + " " + str(ttl)
            if prio > -1:  # Verifica se foi indicado alguma prioridade. Se tiver o valor -1 não foi atribuida.
                string += " " + str(prio)
            arr_extras.append(string)
    extras_f = ",".join(arr_extras)

    data = ";".join((responses_f, authorities_f, extras_f)) + ";"

    # Adiciona as respostas à cache
    all_entries = arr_resp + arr_authorities + arr_extras
    for e in all_entries:
        arr = e.split()
        name = arr[0]
        type_of_value = arr[1]
        value = arr[2]
        ttl = int(arr[3])
        prio = -1
        if len(arr) > 4:
            prio = int(arr[4])
        # Informação relativa ao caching para ser denotado nos logs.
        cache.update(log, name, type_of_value, value, ttl, prio=prio, origin="OTHERS", )

    if n_resp == 0:
        responde_code = 1 # não foi encontrado nenhum type_value relativo a este dominio.

    ## ENVIAR MENSAGEM DE VOLTA OU RETORNAR A STRING DE RESPOSTA PARA O SERVIDOR TRATAR DO ENVIO
    result = ",".join((str(message_id), flags, str(response_code), str(n_resp), str(n_authorities), str(n_extras)))
    result += ";" + q_name + "," + q_type + ";"
    result += data
    return result
    '''

