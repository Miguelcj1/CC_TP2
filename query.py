import time
import auxs
from db_parser import Database
from logs import Logs
from cache import Cache

def pop_end_dot(string):
    if string[-1] == ".":
        return string[:-1]
    return string

# Talvez passar a escolha do ID para dentro desta função.
def init_send_query(id, flag, dom, tipo):
    string = f"{id},{flag},0,0,0,0;{dom},{tipo};"
    return string


def respond_query(query, socket, address, confs, log, dbs, cache):

    log.qr(time.time(), address, query)  # Indica o recebimento de uma query no ficheiro de log.

    arr = query.split(";")

    # Header
    header = arr[0]
    h_fields = header.split(",")
    if len(h_fields) != 6:
        raise Exception(f"Sintaxe desconhecida da seguinte mensagem no header field: {query}")
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
        raise Exception(f"Sintaxe desconhecida da seguinte mensagem no Query Info field: {query}")
    q_name = qi_fields[0]
    q_type = qi_fields[1]

    if len(arr) < 3:
        log.er(time.time(), address, domain=q_name)
        result = f"{message_id},,3,0,0,0;{q_name},{q_type};"  # sendo 3 o código de mensagem não descodificada.
        socket.sendto(result.encode("utf-8"), address)
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

    # Verifica se deve responder a queries deste dominio, relativamente aos DD's.
    respondable_domains = confs.get_all_dd()
    if q_name not in respondable_domains:
        # Não irá ser respondida a query.

        result = f"{message_id},,2,0,0,0;{q_name},{q_type};;"
        log.rp(time.time(), address, result, domain=q_name)
        socket.sendto(result.encode("utf-8"), address)
        return

    # Procura em cache
    result = cache.get_answers(message_id, q_name, q_type)

    # Envio da mensagem para o respetivo endereço
    log.rp(time.time(), address, result, domain=q_name)
    socket.sendto(result.encode("utf-8"), address)


'''
    # Procura e obtenção de respostas na base de dados. ### PARTE EM BAIXO TECNICAMENTE É INUTIL.
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

