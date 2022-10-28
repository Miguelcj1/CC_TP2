import os
import time
import threading

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