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


    # Header
    h_fields = header.split(",")
    if len(h_fields) != 6:
        raise Exception(f"Sintaxe desconhecida da seguinte mensagem no header field: {query}")
    message_id = h_fields[0]
    flags = h_fields[1]
    response_code = h_fields[2]
    n_values = h_fields[3]
    n_authorities = h_fields[4]
    n_extra_values = h_fields[5]

    # Data: Query Info
    qi_fields = data_qi.split(",")
    if len(qi_fields) != 2:
        raise Exception(f"Sintaxe desconhecida da seguinte mensagem no Query Info field: {query}")
    q_name = qi_fields[0]
    q_type = qi_fields[1]


    ''' talvez esta parte seja desnecessaria uma vez que faço isto para queries de perguntas.
    # Terceira parte da mensagem onde vem informaçao de resposta
    # Data: List of Response, Authorities and Extra Values
    resp_fields = data_r.split(",")
    responses = []
    for r in resp_fields:
        responses.append(r)
    '''
    # Talvez atras estive uma procura em cache.
    #pass


    # Procura e obtenção de respostas (MANEIRA PROVISORIA DE TESTE)
    db = dbs.get(pop_end_dot(q_name)) # caso tenha um "." no final, retira-o de maneira a haver coerencia com a maneira que está guardado o valor.
    if db is None:
        # O VALOR NAO FOI ENCONTRADO NA BASE DE DADOS E PROSSEGUIR COM O RESPETIVO PROCEDIMENTO. ###
        # raise Exception("")
        return

    # Identificação do tipo de query
    if q_type == "MX":
        nv = 0
        arr_ans = [] # array de linhas de resposta para serem joined por ","
        mails = db.get_MX(q_name)
        # mails = lista de tuplos (string, int, int)
        for m in mails:
            nv += 1
            string = q_name + " MX " + m[0] + " " + str(m[1]) + " " + str(m[2])
            arr_ans.append(string)
        answers = ",".join(arr_ans)
        t=0


