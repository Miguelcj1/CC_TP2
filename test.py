import os
import time
import threading
import random
import socket




'''
buf = ""
        msg = "1"
        flag = True
        while flag:
            if msg:
                msg = s.recv(1024) # mensagem vem na forma (i;dados)
                msg = msg.decode("utf-8")
                buf += msg
            buf_split = buf.split("\n", 1)
            single_line = buf_split[0]
            if len(buf_split) > 1:
                buf = buf_split[1]
            arr = single_line.split(";")
            n_line = int(arr[0]) # talvez adicionar verificação de ordem ((not sure))
            data = arr[1]
            cache.update_with_line(log, data, "SP")
            if n_line >= lines_to_receive:
                flag = False
        s.send("1".encode("utf-8"))  ### Mensagem de confirmação de todas as linhas recebidas.
        s.close()
        t_end = time.time()
        duracao = t_end - t_start
        log.zt(time.time(), addr, "SS", duracao=duracao, domain=dom)
'''


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
