import os
import sys
import time
import threading
import auxs
from datetime import datetime
from config_parser import Configs


def check_dir(path_arg):
    """
    Esta função verifica a existencia de um ficheiro.
    No caso de o ficheiro não existir, cria o ficheiro e as diretorias onde o ficheiro deverá estar.

    Autor: Pedro Martins.

    :param path_arg: String
    :return: Void
    """
    str = path_arg
    str = str.split("/")[:-1]
    joined_str = "/".join(str)
    exists_file = os.path.exists(path_arg)
    exists_dir = os.path.exists(joined_str)
    if not exists_file and not exists_dir:
        os.makedirs(joined_str)
        f = open(path_arg, "w")  # cria ficheiro
        f.close()
    elif not exists_file:
        f = open(path_arg, "w")  # cria ficheiro
        f.close()


def get_timestamp(timestamp = time.time()):
    """
    Esta função recebe um timestamp e devolve uma string formatada do tempo indicado no timestamp.
    No caso de não receber um timestamp será devolvido a formatação do tempo atual.

    Autor: Pedro Martins.

    :param timestamp: Float
    :return: String
    """
    # convert to datetime
    date_time = datetime.fromtimestamp(timestamp)

    # convert timestamp to string in dd:mm:yyyy.HH:MM:SS:MS
    str_date_time = date_time.strftime("%d:%m:%Y.%H:%M:%S:%f")

    # print("Result 1:", str_date_time[:-3])
    return str_date_time[:-3]


class Logs:
    """
    Esta classe é responsavel pela escrita de todos os logs.
    """

    def __init__(self, confs, mode):
        """
        Esta classe armazena todas as paths para os ficheiros de logs descritos na configuração.
        Para além de escrever nos ficheiros de log existe também o modo "Debug" que permite a visualização do que será escrito no log apartir do terminal.
        A cada dominio também terá de possuir um lock que impedirá problemas de concorrência na escrita dos ficheiros.

        Autor : Miguel Pinto e Pedro Martins.

        :param confs: Configs
        :param mode: String
        """
        # Verifica a existencia do file e caso não exista, cria-o.
        all_log_file = confs.get_all_log_file()
        check_dir(all_log_file)
        self.log_files = {"all": all_log_file}
        self.stdout = True
        self.locks = {"all": threading.Lock()}  # "domain": Lock
        if mode.lower() != "debug":
            self.stdout = False

        for domain in confs.get_domain_names():
            diretoria = confs.get_domain_log_file(domain)
            if diretoria is not None:
                check_dir(diretoria)
                self.log_files[domain] = diretoria
                self.locks[domain] = threading.Lock()


    def check_dom(self, name):
        for k in self.log_files.keys():
            if name.endswith(k):
                return k
        return None


    def qr(self, timestamp, adress, dados, domain = "all"):
        """
        Esta função escreve no log a receção de uma query de um certo domínio.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Pedro Martins.

        :param timestamp: Float
        :param adress: Tuple (endereço, porta)
        :param dados: String
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso não haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log.
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")
            string = f'{get_timestamp(timestamp)} QR {adress} "{dados}"\n'
            fp.write(string)
            fp.close()
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    def qe(self, timestamp, adress, dados, domain = "all"):
        """
        Esta função escreve no log o envio de uma query de um certo domínio.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Miguel Pinto.

        :param timestamp: Float
        :param adress: Tuple (endereço, porta)
        :param dados: String
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")
            #                                        Not sure desta indicaçao do adress.
            string = f'{get_timestamp(timestamp)} QE {str(adress[0])} "{dados}"\n'
            fp.write(string)
            fp.close()
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    # Escreve no log a ocorrencia do envio de uma resposta.
    def rp(self, timestamp, adress, dados, domain = "all"):
        """
        Esta função escreve no log o envio de uma resposta de um certo domínio.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Pedro Martins.

        :param timestamp: Float
        :param adress: Tuple (endereço, porta)
        :param dados: String
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")
            #                                        So vai o endereço sem a porta.
            string = f'{get_timestamp(timestamp)} RP {str(adress[0])} "{dados}"\n'
            fp.write(string)
            fp.close()
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    # Escreve no log a ocorrencia da rececão de uma resposta.
    def rr(self, timestamp, adress, dados, domain = "all"):
        """
        Esta função escreve no log a receção de uma resposta de um certo domínio.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Miguel Pinto.

        :param timestamp: Float
        :param adress: Tuple (endereço, porta)
        :param dados: String
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")

            #                                        Not sure desta indicaçao do adress.
            string = f'{get_timestamp(timestamp)} RR {str(adress[0])} "{dados}"\n'
            fp.write(string)
            fp.close()
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    def zt(self, timestamp, end_adress, papel, duracao=0, domain="all"):
        """
        Esta função escreve no log a conclusão correta de um processo de transferencia de zona.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Pedro Martins.

        :param timestamp: Float
        :param end_adress: String
        :param papel: String
        :param duracao: Float
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")

            #string = get_timestamp(timestamp) + " ZT " + end_adress + " " + papel
            string = f"{get_timestamp(timestamp)} ZT {end_adress} {papel}"
            if duracao > 0:
                duracao = round(duracao, 3)
                string += f" {duracao}ms"
            string += "\n"
            fp.write(string)
            fp.close()

            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    def ev(self, timestamp, info, domain = "all"):
        """
        Esta função escreve no log um determinado evento de um certo domínio.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Miguel Pinto.

        :param timestamp: Float
        :param info: String
        :param domain: String
        :return: Void
        """
        if info is None:
            return
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")

            string = get_timestamp(timestamp) + " EV @ " + info + "\n"
            fp.write(string)
            fp.close()
            # Se for para imprimir no stdout também.
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    def er(self, timestamp, from_adress, dados="", domain="all"):
        """
        Esta função escreve no log que não foi possivel descodificar um PDU corretamente.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Pedro Martins.

        :param timestamp: Float
        :param from_adress: String
        :param dados: String
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")

            #string = get_timestamp(timestamp) + " ER " + from_adress + "\n"
            string = f'{get_timestamp(timestamp)} ER {from_adress} "{dados}"\n'
            fp.write(string)
            fp.close()
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    def ez(self, timestamp, end_adress, papel, domain="all"):
        """
        Esta função escreve no log que o precesso de transferência de zona não foi concluida corretamente.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug", o log será também escrito para o stdout.

        Autor: Miguel Pinto.

        :param timestamp: Float
        :param end_adress: String
        :param papel: String
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")
            #string = get_timestamp(timestamp) + " EZ " + end_adress + " " + papel + "\n"
            string = f"{get_timestamp(timestamp)} EZ {end_adress} {papel}\n"
            fp.write(string)
            fp.close()
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    def fl(self, timestamp, info, domain="all"):
        """
        Esta função escreve no log que ocurreu um erro no funcionamento interno de um componente.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Pedro Martins.

        :param timestamp: Float
        :param info: String
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")

            string = get_timestamp(timestamp) + " FL 127.0.0.1 " + info + "\n"
            fp.write(string)
            fp.close()
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    def to(self, timestamp, adress, info, domain="all"):
        """
        Esta função escreve no log a ocurrência de um timeout na interação com um servidor.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Miguel Pinto.

        :param timestamp: Float
        :param adress: String
        :param info: String
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")

            #string = get_timestamp(timestamp) + " TO " + adress + " " + info + "\n"
            string = f"{get_timestamp(timestamp)} TO {adress} {info}\n"
            fp.write(string)
            fp.close()
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    def sp(self, timestamp, info, domain="all"):
        """
        Esta função escreve no log que a execução de um componente parou.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Pedro Martins.

        :param timestamp: Float
        :param info: String
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")

            string = get_timestamp(timestamp) + " SP 127.0.0.1 " + info + "\n"
            fp.write(string)
            fp.close()
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()


    def st(self, timestamp, port, timeout, mode, domain = "all"):
        """
        Esta função escreve no log que a execução de um componente foi iniciado.
        Todas as escritas nos ficheiros necessitam da obtenção do lock e no caso de estar em modo "Debug" o log será escrito também no stdout.

        Autor: Miguel Pinto.

        :param timestamp: Float
        :param port: Int
        :param timeout: Int
        :param mode: String
        :param domain: String
        :return: Void
        """
        domain = self.check_dom(domain)
        if domain is None:
            domain = "all" # caso n haja nenhuma especificação de log para este domínio, vai para o ficheiro all_log
        self.locks[domain].acquire()
        try:
            fp = open(self.log_files[domain], "a")

            timeout *= 1000
            string = f"{get_timestamp(timestamp)} ST 127.0.0.1 {port} {timeout} {mode}\n"
            fp.write(string)
            fp.close()
            if self.stdout:
                sys.stdout.write(string)
        finally:
            self.locks[domain].release()

