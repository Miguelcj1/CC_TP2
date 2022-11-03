import random
import time
import auxs
from db_parser import Database
from logs import Logs

def pop_end_dot(string):
    if string[-1] == ".":
        return string[:-1]
    return string

def init_send_query(id, flag, dom, type):
    string = ",".join((str(id), flag)) + ",0,0,0,0;" + ",".join((dom, type)) + ";"
    return string

# raises exception in which is caused by a problem in decoding the received string (ER ou FL)
def respond_query(query, dbs):

    arr = query.split(";")
    if len(arr) < 3:
        raise Exception(f"Sintaxe desconhecida da seguinte mensagem: {query}")

    header = arr[0]
    data_qi = arr[1]
    response_qi = arr[2]

    # Header
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
    qi_fields = data_qi.split(",")
    if len(qi_fields) != 2:
        raise Exception(f"Sintaxe desconhecida da seguinte mensagem no Query Info field: {query}")
    q_name = qi_fields[0]
    q_type = qi_fields[1]


    #talvez esta parte seja desnecessaria uma vez que faço isto para queries de perguntas.
    # Terceira parte da mensagem onde vem informaçao de resposta
    # Data: List of Response, Authorities and Extra Values
    if response_qi:
        resp_fields = response_qi.split(",")
        responses = []
        for r in resp_fields:
            responses.append(r)


    # Procura e obtenção de respostas
    db = dbs.get(q_name)
    if db is None:
        # O VALOR NAO FOI ENCONTRADO NA BASE DE DADOS E PROSSEGUIR COM O RESPETIVO PROCEDIMENTO. ###
        # raise Exception("")
        return

    all_values = []
    responses_f = None
    n_resp = 0
    arr_resp = []
    n_authorities = 0
    arr_authorities = []
    n_extras = 0
    arr_extras = []

    # Identificação do tipo de query

    if q_type in ["SOASP", "SOAADMIN", "SOASERIAL", "SOAREFRESH", "SOARETRY", "SOAEXPIRE"]:
        # Obtencao de response_values
        responses_f = db.get_SOA_(q_type, q_name)

    elif q_type == "NS":
        # Obtencao de response_values
        valores = db.get_NS(q_name)
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

    elif q_type == "A":
        # Obtencao de response_values
        valores = db.get_A(q_name)
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

    elif q_type == "CNAME":
        # Obtencao de response_values
        valores = db.get_NS(q_name)
        # valores = lista de tuplos (string, int, int)
        for v in valores:
            n_resp += 1
            value = v[0]
            ttl = v[1]
            string = q_name + " MX " + value + " " + str(ttl)
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
        valores = db.get_NS(q_name)
        # valores = lista de tuplos (string, int, int)
        for v in valores:
            n_resp += 1
            value = v[0]
            ttl = v[1]
            string = q_name + " MX " + value + " " + str(ttl)
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

    data = ";".join((responses_f, authorities_f, extras_f))

    ## ENVIAR MENSAGEM DE VOLTA OU RETORNAR A STRING DE RESPOSTA PARA O SERVIDOR TRATAR DO ENVIO


