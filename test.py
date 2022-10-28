import os

dict = {1: 23, 2: 334, 4: 3213, 6: 1234}
arr = [1, 2, 3]

x = len(arr)
print(x)

chx = 0
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