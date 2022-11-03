import random
import time
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


    # Procura e obtenção de respostas (MANEIRA PROVISORIA DE TESTE)
    db = dbs.get(pop_end_dot(q_name)) # caso tenha um "." no final, retira-o de maneira a haver coerencia com a maneira que está guardado o valor.
    if db is None:
        # O VALOR NAO FOI ENCONTRADO NA BASE DE DADOS E PROSSEGUIR COM O RESPETIVO PROCEDIMENTO. ###
        # raise Exception("")
        return

    # Identificação do tipo de query
    if q_type == "MX":
        # Aqui estaria uma procura em cache talvez, antes de verificar na base de dados.

        all_values = []

        # Obtencao de response_values
        n_resp = 0 ### estas variaveis talvez devessem estar antes destes ifs
        arr_resp = [] # array de linhas de resposta para serem joined por ","
        mails = db.get_MX(q_name)
        # mails = lista de tuplos (string, int, int)
        for m in mails:
            n_resp += 1
            string = q_name + " MX " + m[0] + " " + str(m[1]) + " " + str(m[2])
            all_values.append(m[0])
            arr_resp.append(string)
        responses_f = ",".join(arr_resp)

        # Obtencao de authority_values
        n_authorities = 0
        arr_authorities = []
        authorities = db.get_NS(q_name)
        for a in authorities:
            n_authorities += 1
            string = q_name + " NS " + a[0] + " " + str(a[1]) + " " + str(a[2])
            all_values.append(a[0])
            arr_authorities.append(string)
        authorities_f = ",".join(arr_authorities)

        # Obtencao de extra_values
        n_extras = 0
        arr_extras = []
        for v in all_values:
            extras = db.get_A(v)
            for e in extras:
                n_extras += 1
                string = v + " A " + e[0] + " " + str(e[1]) + " " + str(e[2])
                arr_extras.append(string)
            extras_f = ",".join(arr_extras)

        data = ";".join((responses_f, authorities_f, extras_f))

    ## ENVIAR MENSAGEM DE VOLTA OU RETORNAR A STRING DE RESPOSTA PARA O SERVIDOR TRATAR DO ENVIO


