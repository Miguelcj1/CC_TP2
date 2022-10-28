import os


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

class DomainInfo:

    def __init__(self): # acho inutil ter aqui o nome do dominio a que se refere, mas talvez possa ser util.
        self.database_path = None
        self.log_file = None
        self.sp = None
        self.ss = []
        self.dd = []

    # Se já houver uma referência de base de dados para este dominio, retorna falso para indicar uma incoerencia no ficheiro.
    def set_db(self, db_path):
        if self.database_path is None:
            self.database_path = db_path
            return True
        else:
            print("ERRO!! False SET_DB") ###
            return False

    # Get the domain info database
    def get_db(self):
        if self.database_path:
            return self.database_path
        else:
            print("Error: wasnt found a database for the domain")
            return None

    # Se já houver uma referência de ficheiro de log para este dominio, retorna falso para indicar uma incoerencia no ficheiro.
    def set_log_file(self, log_path):
        if self.log_file is None:
            self.log_file = log_path
            return True
        else:
            print("ERRO!! False SET_LOG_FILE")  ###
            return False

    # Get the domain info log_file
    def get_log_file(self):
        if self.log_file:
            return self.log_file
        else:
            print("Error: wasnt found a log file for the domain")
            return None

    # Se já houver uma referência de SP para este dominio, retorna falso para indicar uma incoerencia no ficheiro.
    def set_sp(self, sp):
        if self.sp is None:
            self.sp = sp
            return True
        else:
            print("ERRO!! False SET_SP")  ###
            return False

    # Get the domain info SP
    def get_sp(self):
        if self.sp:
            return self.sp
        else:
            print("Error: wasnt found a SP for the domain")
            return None

    # Adiciona à lista de SS's, o argumento passado.
    def add_ss(self, ss):
        self.ss.append(ss)

    # Get the domain info SS
    def get_ss(self):
        if self.ss:
            return self.ss
        else:
            print("Error: wasnt found a SS for the domain")
            return None

    # Adiciona à lista de SS's, o argumento passado.
    def add_dd(self, dd):
        self.dd.append(dd)

    # Get the domain info DD
    def get_dd(self):
        if self.dd:
            return self.dd
        else:
            print("Error: wasnt found a DD for the domain")
            return None


class Configs:

    # Define as diversas variavéis analisadas no ficheiro de configuração.
    def __init__(self, conf_file):
        self.st_file_path = None
        self.domains = {}
        self.all_log = None

        ## Leitura e análise do ficheiro inicial de configuração.
        try:
            fp = open(conf_file, "r")
        except FileNotFoundError:
            print("Configuration file not found!")
            return None

        for line in fp:
            arr = line.split()
            # Verifica se a linha está vazia ou começa por '#'.
            if not line.strip() or arr[0].startswith("#"):
                pass  # does nothing = nop

            elif arr[1] == "DB": # (((talvez tenha de fazer uma verificação da length de arr para n dar seg fault.)))
                domain = arr[0]
                # uso o pop_slash para remover o primeiro "/" de modo a ter a diretoria de maneira correta
                db_path = pop_slash(arr[2])
                if self.domains.get(domain) is None:
                    self.domains[domain] = DomainInfo()

                if not self.domains[domain].set_db(db_path):
                    print("Incoerencia no set_db!")
                    return None # nestes return none talvez faltasse fazer o fp.close() antes.

            elif arr[1] == "SP":
                domain = arr[0]
                sp = arr[2]
                if self.domains.get(domain) is None:
                    self.domains[domain] = DomainInfo()
                # talvez pudesse mandar um tuplo (endereço, porta) e caso nao houvesse porta, mandava None no lugar da porta.
                if not self.domains[domain].set_sp(sp):
                    print("Incoerencia no set_sp!")
                    return None

            elif arr[1] == "SS":
                domain = arr[0]
                ss = arr[2]
                if self.domains.get(domain) is None:
                    self.domains[domain] = DomainInfo()
                self.domains[domain].add_ss(ss)


            elif arr[1] == "DD":
                domain = arr[0]
                dd = arr[2]
                if self.domains.get(domain) is None:
                    self.domains[domain] = DomainInfo()
                self.domains[domain].add_dd(dd)

            elif arr[1] == "ST":
                if arr[0] != "root":
                    # mensagem de erro, pois o parametro deve ser igual a "root".
                    print("ERRO, o parametro de ST deve ser igual a root!!")
                    return None
                elif self.st_file_path is None:
                    self.st_file_path = pop_slash(arr[2])
                else:
                    # mensagem de erro, pois há mais que uma indicação de ST filepaths.
                    print("ERRO!! Pois há mais que uma indicação de ST filepaths!")
                    return None

            elif arr[1] == "LG":
                domain = arr[0]
                # uso o pop_slash para remover o primeiro "/" de modo a ter a diretoria de maneira correta
                log_path = pop_slash(arr[2])
                if domain == "all":
                    self.all_log = log_path
                # Verfifica se o dominio existe no contexto deste servidor.
                elif self.domains.get(domain) is None:
                    print(f"Error! This server is not responsible for the domain {domain}!")
                    return None
                # Define o log_file do determinado dominio.
                elif not self.domains[domain].set_log_file(log_path):
                    print("Incoerencia no set_log_file!")
                    return None

            else:
                print("!Passou no else do config_parser!")
                pass

        fp.close()

        '''
        # Acho que não é preciso fazer isto
        # Define em todos os dominios, o respetivo ficheiro de log, assigned "all". 
        if self.all_log is not None:
            for key in self.domains:
                if self.domains[key].get_log_file() is None:
                    self.domains[key].set_log_file(self.all_log)
        '''

        # Restrição de haver log file para todos os dominios.
        for key in self.domains:
            if self.domains[key].get_log_file is None:
                print(f"O domínio {key} não tem log file!!")
                return None

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
            return self.domains[domain].get_sp()
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
        if self.domains[domain].get_db():
            return self.domains[domain].get_db()
        else:
            print("!get_db_path não obteve nenhuma referencia a base de dados!")
            return None

    # Retorna o path do ficheiro de log de um determinado dominio.
    def get_domain_log_file(self, domain):
        if self.domains[domain].get_log_file():
            return self.domains[domain].get_log_file()
        else:
            print("!get_db_path não obteve nenhuma referencia a base de dados!")
            return None

    def get_all_log_file(self):
        return self.all_log

    # Retorna o path do ficheiro dos servidores de topo.
    def get_st_file(self):
        return self.st_file_path
