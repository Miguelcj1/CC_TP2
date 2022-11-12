import os
import time
import threading
import random
import socket


res = "andre"

try:
    inteiro = int(res)
except ValueError:
    print("Ola")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(res.encode("utf-8"), ("127.0.0.1", 5001))


'''
    ### TESTE ###
    # constroi uma string no formato da mensagem que vai ser transmitida.
    #cache = Cache()
    id = 12
    q = query.init_send_query(id, "Q+A", "example.com.", "MX")
    res = query.respond_query(q, confs, databases, cache, log)

    ### FIM ###
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
