import os
import time
from datetime import datetime


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



# Função que retorna a string formatada do tempo atual. Pode receber uma timestamp como argumento, caso contrário, irá ser calculado relativamente ao tempo atual.
def get_timestamp(timestamp = time.time()):
    # convert to datetime
    date_time = datetime.fromtimestamp(timestamp)

    # convert timestamp to string in dd:mm:yyyy.HH:MM:SS:MS
    str_date_time = date_time.strftime("%d:%m:%Y.%H:%M:%S:%f")

    # print("Result 1:", str_date_time[:-3])
    return str_date_time[:-3]


# esta classe escreve os logs no ficheiro de log indicado na sua variavel de instância.
class Logs:

    # Verifica a diretoria do ficheiro de log e define o caminho na sua variavel de instancia.
    def __init__(self, file):
        # verifica a existencia do file e caso não exista, cria-o
        check_dir(file)
        self.log_file = file

    # método que escreve no log a ocorrencia da receçao de uma query
    def qr(self, timestamp, adress, dados):
        try:
            fp = open(self.log_file, "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        string = get_timestamp(timestamp) + " QR " + str(adress[0]) + " [" + dados + "]\n"
        fp.write(string)
        fp.close()

    # método que escreve no log a ocorrencia do envio de uma query
    def qe(self, timestamp, adress, dados):
        try:
            fp = open(self.log_file, "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        #                                          Not sure desta indicaçao do adress.
        string = get_timestamp(timestamp) + " QE " + str(adress[0]) + " [" + dados + "]\n"
        fp.write(string)
        fp.close()

    #definir outros metodos das possiveis linhas existentes num log...


