import os
import auxs


# remove o "/" inicial de uma string.
def pop_slash(string):
    if string[0] == "/":
        final = string.replace('/', '', 1)
    else:
        final = string
    return final


# Create/Open directory
def co_dir(path, mode):
    str = path
    str = str.split("/")[:-1]
    joined_str = "/".join(str)
    if os.path.exists(path):
        f = open(path, mode)
    else:
        os.makedirs(joined_str)
        f = open(path, mode)
    return f

# Retorna None caso não seja indicado a porta do SP
def str_adress_to_tuple(string):
    arr = string.split(":")
    if len(arr) < 2:
        return None
    res = (arr[0], int(arr[1]))
    return res


class DomainInfo:

    def __init__(self):
        self.name = None
        self.database_path = None
        self.log_file = None
        self.sp = None
        self.ss = []
        self.dd = []


    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    # Se já houver uma referência de base de dados para este dominio, retorna falso para indicar uma incoerencia no ficheiro.
    def set_db(self, db_path):
        if self.database_path is None:
            self.database_path = db_path
            return True
        else:
            return False

    # Get the domain info database
    def get_db(self):
        if self.database_path:
            return self.database_path
        else:
            return None

    # Se já houver uma referência de ficheiro de log para este dominio, retorna falso para indicar uma incoerencia no ficheiro.
    def set_log_file(self, log_path):
        if self.log_file is None:
            self.log_file = log_path
            return True
        else:
            return False

    # Get the domain info log_file
    def get_log_file(self):
        if self.log_file:
            return self.log_file
        else:
            return None

    # Se já houver uma referência de SP para este dominio, retorna falso para indicar uma incoerencia no ficheiro.
    def set_sp(self, sp):
        if self.sp is None:
            self.sp = sp
            return True
        else:
            return False

    # Get the domain info SP
    def get_sp(self):
        if self.sp:
            return self.sp
        else:
            return None

    # Adiciona à lista de SS's, o argumento passado.
    def add_ss(self, ss):
        self.ss.append(ss)

    # Get the domain info SS
    def get_ss(self):
        if self.ss:
            return self.ss
        else:
            return None

    # Adiciona à lista de DD's, o argumento passado.
    def add_dd(self, dd):
        self.dd.append(dd)

    # Get the domain info DD
    def get_dd(self):
        if self.dd:
            return self.dd
        else:
            return None


class Configs:

    # Define as diversas variavéis analisadas no ficheiro de configuração.
    def __init__(self, conf_file):
        self.st_file_path = None
        self.all_log = None
        self.domains = {}
        #self.sp = [] # nomes do dominios em que o servidor atua como servidor principal
        #self.ss = [] # nomes do dominios em que o servidor atua como servidor secundario

        ## Leitura e análise do ficheiro inicial de configuração.
        try:
            fp = open(conf_file, "r")
        except FileNotFoundError:
            raise Exception("Configuration file not found!")

        for line in fp:
            arr = line.split()

            # Verifica se a linha está vazia ou começa por '#'.
            if not line.strip() or arr[0].startswith("#"):
                continue

            domain = arr[0]
            if domain != "all":
                domain = auxs.add_end_dot(arr[0]) # ADICIONA O "." nas configurações também!

            if arr[1] == "DB" and len(arr) == 3:
                # uso o pop_slash para remover o primeiro "/" de modo a ter a diretoria de maneira correta
                db_path = pop_slash(arr[2])
                if self.domains.get(domain) is None:
                    self.domains[domain] = DomainInfo()
                self.domains[domain].set_name(domain)
                if not self.domains[domain].set_db(db_path):
                    raise Exception(f"Ocorreu mais que uma definição da base de dados do dominio {domain}!")

            elif arr[1] == "SP" and len(arr) == 3:
                sp = arr[2]
                if self.domains.get(domain) is None:
                    self.domains[domain] = DomainInfo()
                self.domains[domain].set_name(domain)
                # Coloca um tuplo
                addr = str_adress_to_tuple(sp)  # retorna None caso não seja indicada uma porta.
                if addr is None:
                    raise Exception(f"É necessário especificar a porta do servidor primário do domínio {domain}.")
                if not self.domains[domain].set_sp(addr):
                    raise Exception(f"Ocorreu mais que uma definição do servidor principal do dominio {domain}.")

            elif arr[1] == "SS" and len(arr) == 3:
                ss = arr[2]
                if self.domains.get(domain) is None:
                    self.domains[domain] = DomainInfo()
                self.domains[domain].set_name(domain)
                self.domains[domain].add_ss(ss)

            elif arr[1] == "DD" and len(arr) == 3:
                dd = arr[2]
                if self.domains.get(domain) is None:
                    self.domains[domain] = DomainInfo()
                self.domains[domain].set_name(domain)
                self.domains[domain].add_dd(dd)

            elif arr[1] == "ST" and len(arr) == 3:
                if arr[0] != "root":
                    # mensagem de erro, pois o parametro deve ser igual a "root".
                    raise Exception("ERRO, o parametro de ST deve ser igual a root!!")
                elif self.st_file_path is None:
                    self.st_file_path = pop_slash(arr[2])
                else:
                    # mensagem de erro, pois há mais que uma indicação de ST filepaths.
                    raise Exception("ERRO!! Pois há mais que uma indicação de ST filepaths!")

            elif arr[1] == "LG" and len(arr) == 3:

                # uso o pop_slash para remover o primeiro "/" de modo a ter a diretoria de maneira correta
                log_path = pop_slash(arr[2])
                if domain == "all":
                    self.all_log = log_path

                # Verfifica se o dominio existe no contexto deste servidor.
                elif self.domains.get(domain) is None:
                    raise Exception(f"Error! This server is not responsible for the domain {domain}!")

                # Define o log_file do determinado dominio.
                elif not self.domains[domain].set_log_file(log_path):
                    raise Exception(f"Ocorreu mais que uma definição do log_file do dominio {domain}!")

            else:
                raise Exception(f"Erro! Sintaxe desconhecida na seguinte linha: {line}.")

        fp.close()

        '''
        # Restrição de haver log file para todos os dominios.
        for key in self.domains:
            if self.domains[key].get_log_file is None:
                raise Exception(f"O domínio {key} não tem log file!!")'''

    # Verifica se o server é Principal para um determinado domínio.
    def is_sp(self, domain):
        if self.domains[domain].get_sp() is None:
            return True
        else:
            return False

    # Retorna o endereço do servidor principal de um determinado domínio, caso não seja ele proprio
    def get_sp(self, domain):
        if self.domains[domain].get_sp():
            return self.domains[domain].get_sp()
        else:
            print("!get_sp não obteve nenhum sp!")
            return None

    # Retorna o endereço do servidor principal de um determinado domínio, caso não seja ele proprio
    def get_ss(self, domain):
        if self.domains[domain].get_ss():
            return self.domains[domain].get_ss()
        else:
            print("!get_ss não obteve nenhum ss!")
            return None

    # Retorna o endereço do servidor principal de um determinado domínio, caso não seja ele proprio
    def get_dd(self, domain):
        if self.domains[domain].get_dd():
            return self.domains[domain].get_dd()
        else:
            print("!get_dd não obteve nenhum dd!")
            return None

    # Retorna o path do ficheiro de base de dados.
    def get_db_path(self, domain):
        return self.domains[domain].get_db()


    # Retorna o path do ficheiro de log de um determinado dominio.
    def get_domain_log_file(self, domain):
        if self.domains[domain].get_log_file():
            return self.domains[domain].get_log_file()
        else:
            #print("!get_db_path não obteve nenhuma referencia a base de dados!")
            return None

    def get_all_log_file(self):
        return self.all_log

    # talvez isto fosse verificar as entradas DD se for um SP ou SS, para ver quais os dominios que pode responder. ### TALVEZ A FUNCAO DE BAIXO INUTILIZE ESTA
    # Obtem todos os dominios mencionados no ficheiro de configuração
    def get_domain_names(self):
        ret = []
        for key in self.domains:
            if key != "all":
                ret.append(key)
        return ret

    # Retorna todos os dominios que têm uma entrada DD, ou seja, todos os dominios que o server pode responder.
    def get_all_dd(self):
        ret = []
        for key in self.domains:
            if key != "all" and self.domains[key].get_dd():
                ret.append(key)
        return ret

    # Retorna o path do ficheiro dos servidores de topo.
    def get_st_file(self):
        return self.st_file_path

    # Retorna uma lista com os nomes dos dominios que não tem um servidor principal no DomainInfo.
    def get_sp_domains(self):
        result = []
        for value in self.domains.values():
            if value.get_sp() is None:
                dom = value.get_name()
                result.append(dom)
        return result

    # Retorna uma lista com os nomes dos dominios que tem um servidor principal no DomainInfo.
    def get_ss_domains(self):
        result = []
        for value in self.domains.values():
            if value.get_sp() is not None:
                dom = value.get_name()
                result.append(dom)
        return result



