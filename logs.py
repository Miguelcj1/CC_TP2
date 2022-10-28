import os
import time
from datetime import datetime
from config_parser import Configs


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
    def __init__(self, confs):
        # Verifica a existencia do file e caso não exista, cria-o.
        all_log_file = confs.get_all_log_file()
        check_dir(all_log_file)
        self.log_files = {"all": all_log_file}

        for domain in confs.get_domains():
            diretoria = confs.get_domain_log_file(domain)
            check_dir(diretoria)
            self.log_files[domain] = diretoria

    ## talvez juntar estas 4 primeiras funcoes porque fazem o mesmo exceto nas letras do tipo de entrada.
    ## talvez adicionar printf nestes metodos porque vai ser necessario tambem fazer print para o terminal, ou talvez guardar uma flag no objeto para ver se querem que se faça print no terminal.
    # Escreve no log a ocorrencia da receçao de uma query.
    def qr(self, timestamp, adress, dados, domain = "all"):
        try:
            fp = open(self.log_files[domain], "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        string = get_timestamp(timestamp) + " QR " + str(adress[0]) + " [" + dados + "]\n"
        fp.write(string)
        fp.close()

    # Escreve no log a ocorrencia do envio de uma query
    def qe(self, timestamp, adress, dados, domain = "all"):
        try:
            fp = open(self.log_files[domain], "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        #                                          Not sure desta indicaçao do adress.
        string = get_timestamp(timestamp) + " QE " + str(adress[0]) + " [" + dados + "]\n"
        fp.write(string)
        fp.close()

    # Escreve no log a ocorrencia do envio de uma query
    def rp(self, timestamp, adress, dados, domain = "all"):
        try:
            fp = open(self.log_files[domain], "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        #                                          Not sure desta indicaçao do adress.
        string = get_timestamp(timestamp) + " RP " + str(adress[0]) + " [" + dados + "]\n"
        fp.write(string)
        fp.close()

    # Escreve no log a ocorrencia do envio de uma query
    def rr(self, timestamp, adress, dados, domain = "all"):
        try:
            fp = open(self.log_files[domain], "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        #                                          Not sure desta indicaçao do adress.
        string = get_timestamp(timestamp) + " RR " + str(adress[0]) + " [" + dados + "]\n"
        fp.write(string)
        fp.close()

    # Reporta a conclusao correta de um processo de transferencia de zona.
    #end_adress -> o servidor na outra ponta da transferência
    #papel -> papel do servidor local na transferência (SP ou SS)
    #(OPCIONAL) duracao da transferencia e total de bytes transferidos
    def zt(self, timestamp, end_adress, papel, domain="all"):
        try:
            fp = open(self.log_files[domain], "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        string = get_timestamp(timestamp) + " ZT " + end_adress + " " + papel + "\n"
        fp.write(string)
        fp.close()

    # Reporta um determinado evento.
    def ev(self, timestamp, info, domain = "all"):
        try:
            fp = open(self.log_files[domain], "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        #                                          Not sure desta indicaçao do adress.
        string = get_timestamp(timestamp) + " EV @ " + info + "\n"
        fp.write(string)
        fp.close()

    # (ERRO) Reporta a impossibilidade de descodificar um PDU corretamente.
    #Outras opcionalidades
    def er(self, timestamp, from_adress, domain="all"):
        try:
            fp = open(self.log_files[domain], "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        string = get_timestamp(timestamp) + " ER " + from_adress + "\n"
        fp.write(string)
        fp.close()

    # (ERRO DE ZONA) Reporta a conclusao incorreta de um processo de transferencia de zona.
    def ez(self, timestamp, end_adress, papel, domain="all"):
        try:
            fp = open(self.log_files[domain], "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        string = get_timestamp(timestamp) + " ZT " + end_adress + " " + papel + "\n"
        fp.write(string)
        fp.close()

    # (SERVIDOR PAROU) Reporta que a execução do componente foi parado.
    def sp(self, timestamp, info, domain="all"):
        try:
            fp = open(self.log_files[domain], "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        string = get_timestamp(timestamp) + " SP 127.0.0.1 " + info + "\n"
        fp.write(string)
        fp.close()

    # Reporta o arranque do servidor ((Not sure donde virao os valores do ttl e o mode)). NOT SURE
    def st(self, timestamp, port, ttl, mode, domain = "all"):
        try:
            fp = open(self.log_files[domain], "a")
        except FileNotFoundError:
            print("Logging file not found!!")
            return None
        string = get_timestamp(timestamp) + " ST 127.0.0.1 " + str(port) + " " + str(ttl) + " " + mode + "\n"
        fp.write(string)
        fp.close()

