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

class Configs:

    # Define as diversas variavéis analisadas no ficheiro de configuração.
    def __init__(self, conf_file):
        self.database_path = None
        self.st_file_path = None
        self.log_file = "/var/dns/logfile.log"  # path standard do ficheiro que deve ser criado.
        self.sp = None
        self.ss = []
        self.dd = []

        ## Leitura e análise do ficheiro inicial de configuração.
        try:
            fp = open(conf_file, "r")
        except FileNotFoundError:
            print("Configuration file not found!")
            return None

        for line in fp:
            arr = line.split()
            if arr[0].startswith("#"):
                pass  # does nothing = nop
            elif arr[1] == "DB":
                self.database_path = pop_slash(arr[2])  # uso o pop_slash para remover o primeiro "/" de modo a ter a diretoria de maneira correta
            elif arr[1] == "SP":
                if self.sp is None:
                    self.sp = arr[2]
                else:
                    print("ERRO! Há mais que um servidor primario a ser configurado!!")  # mensagem de erro.
                    return None
            elif arr[1] == "SS":
                self.ss.append(arr[2])  # porta incluida na string
            elif arr[1] == "DD":
                self.dd.append(arr[2])  # porta incluida na string
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

            elif arr[1] == "LG":  # faltam particularidades tendo em conta o domínio, eu acho
                self.log_file = pop_slash(arr[2])
            else:
                print("!Passou no else do config_parser!")
                pass

        fp.close()

    # Função verifica nas configurações se se trata dum servidor primario.
    # ou seja, verifica se encontrou algum valor de SP.
    def is_sp(self):
        if self.sp is None:
            return True
        else:
            return False

    # Retorna o endereço do servidor principal, caso não seja ele proprio
    def get_sp(self):
        if self.sp:
            return self.sp
        else:
            print("!get_sp não obteve nenhum sp!")
            return None

    # Retorna o path do ficheiro de base de dados.
    def get_db_path(self):
        return self.database_path

    # Retorna o path do ficheiro dos servidores de topo.
    def get_st_file(self):
        return self.st_file_path

    # Retorna o path do ficheiro de log.
    def get_log_file_path(self):
        return self.log_file