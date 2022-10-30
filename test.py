import os
import time
import threading


# raises exception in which is caused by a problem in decoding the received string (ER ou FL)
def respond_querry(string):
    arr = string.split(";")
    if len(arr) != 3:
        raise Exception(f"Sintaxe desconhecida da seguinte mensagem: {string}")

    header = arr[0]
    data_qi = arr[1]
    data_r = arr[2]

    # Header
    h_fields = header.split(",")
    if len(h_fields) != 6:
        raise Exception(f"Sintaxe desconhecida da seguinte mensagem no header field: {string}")
    message_id = h_fields[0]
    flags = h_fields[1]
    response_code = h_fields[2]
    n_values = h_fields[3]
    n_authorities = h_fields[4]
    n_extra_values = h_fields[5]

    # Data: Query Info
    qi_fields = data_qi.split(",")
    if len(qi_fields) != 2:
        raise Exception(f"Sintaxe desconhecida da seguinte mensagem no Query Info field: {string}")
    q_name = qi_fields[0]
    q_type = qi_fields[1]
    t = 0

def init_send_querry(id, flag, dom, type):
    string = ",".join((str(id), flag)) + ",0,0,0,0;" + ",".join((dom, type)) + ";"
    return string

q = init_send_querry(12, "Q+A", "example.com.", "MX")
print(q)

respond_querry(q)

tup = ("oi", 23, 12)
print(" ".join(tup))

'''
# teste de threads que funciona.
def del_in(dict, key, t):
    time.sleep(t)
    del dict[key]
    print(dict)

def add(dict, key, value, t):
    dict[key] = value
    threading.Thread(target=del_in, args=(dict, key, t)).start()
    print("Passei aqui!")
    print(dict)

key = 7
value = 143
dict = {1: 23, 2: 2323, 3: 323, 4: 65, 5: 43, 6: 54}
add(dict, key, value, 10)
'''

'''
# checks and creates directory
def check_dir(path_arg):
    str = path_arg
    str = str.split("/")[:-1]
    joined_str = "/".join(str)
    exists_file = os.path.exists(path_arg)
    exists_dir = os.path.exists(joined_str)
    if not exists_file and not exists_dir:
        os.makedirs(joined_str)
        f = open(path_arg, "w")  # cria ficheiro
        f.close()
        print(f"[DEBUG] Diretoria e ficheiro criado {path_arg}.") ##
    elif not exists_file:
        f = open(path_arg, "w")  # cria ficheiro
        f.close()
        print(f"[DEBUG] Ficheiro criado {path_arg}.")  ##
    else:
        print(f"[DEBUG] Diretoria {path_arg} já estava criada.") ##

path = "var/dns/all.log"
check_dir(path)
'''
