import os
import auxs


def pop_slash(string):
    """
    Esta função remove o "/" inicial de uma string.

    Autor Pedro Martins.

    :param string: String
    :return: String
    """
    if string[0] == "/":
        final = string.replace('/', '', 1)
    else:
        final = string
    return final


def co_dir(path, mode):
    """
    Esta função abre um ficheiro. No caso de não existir a path para esse ficheiro são criadas as diretorias descritas na path.

    Autor: Pedro Martins.

    :param path: String
    :param mode: String
    :return: File
    """
    str = path
    str = str.split("/")[:-1]
    joined_str = "/".join(str)
    if os.path.exists(path):
        f = open(path, mode)
    else:
        os.makedirs(joined_str)
        f = open(path, mode)
    return f

# Dado um "endereço" ou "endereço:porta" retorna o tuplo (endereco, porta)
def str_adress_to_tuple(string, default_port = 5000):
    """
    Esta função recebe um endereço e opcionalmente uma porta e cria um tuplo (endereço, porta).

    Autor: Pedro Martins.

    :param string: String
    :param default_port: Int
    :return: Tuple (endereço, porta)
    """
    arr = string.split(":")
    if len(arr) < 2:
        res = (arr[0], default_port)
        return res
    res = (arr[0], int(arr[1]))
    return res


class DomainInfo:
    """
    Esta classe é responsável por armazenar os dados vindos do ficheiro de configuração, relativos a um determinado domínio.
    """

    def __init__(self):
        """
        Esta classe possui o nome, path da base de dados e a path do ficheiro de log de um certo dominio.
        Possui também os endereços relativos ao SP, SS, e SR pertencentes a esse dominio.

        Autor: Miguel Pinto e Pedro Martins.

        """
        self.name = None
        self.database_path = None
        self.log_file = None
        self.sp = None
        self.ss = []
        self.dd = []


    def set_name(self, name):
        """
        Função de set do nome do dominio.

        Autor: Pedro Martins.

        :param name: String
        :return: Void
        """
        self.name = name

    def get_name(self):
        """
        Função de get do nome do dominio.

        Autor: Pedro Martins

        :return: String
        """
        return self.name

    def set_db(self, db_path):
        """
        Função de set da path da base de dados do dominio.
        Retorna falso caso já exista uma path para uma base de dados deste dominio.

        Autor: Pedro Martins.


        :param db_path: String
        :return: Boolean
        """
        if self.database_path is None:
            self.database_path = db_path
            return True
        else:
            return False

    def get_db(self):
        """
        Função de get da path da base de dados do dominio.

        Autor: Pedro Martins.

        :return: String
        """
        if self.database_path:
            return self.database_path
        else:
            return None

    def set_log_file(self, log_path):
        """
        Função de set da path do ficheiro de log do dominio.
        Retorna false caso já exista uma path para um ficheiro de log deste dominio.

        Autor: Pedro Martins.

        :param log_path: String
        :return: Boolean
        """
        if self.log_file is None:
            self.log_file = log_path
            return True
        else:
            return False

    def get_log_file(self):
        """
        Função de get da path do ficheiro de log do dominio.

        Autor: Pedro Martins.

        :return: String
        """
        if self.log_file:
            return self.log_file
        else:
            return None

    def set_sp(self, sp):
        """
        Função de set do SP do dominio.
        Retorna false caso ja exista um SP deste dominio.

        Autor: Pedro Martins.

        :param sp:
        :return: Boolean
        """
        if self.sp is None:
            self.sp = sp
            return True
        else:
            return False

    def get_sp(self):
        """
        Função de get do SP do dominio.

        Autor: Pedro Martins.

        :return: String
        """
        if self.sp:
            return self.sp
        else:
            return None

    def add_ss(self, ss):
        """
        Função de que adiciona um SS à lista de SS deste dominio.

        Autor: Pedro Martins.

        :param ss: String
        :return: Void
        """
        self.ss.append(ss)

    def get_ss(self):
        """
        Função que retorna a lista de SS deste dominio.

        Autor: Pedro Martins.

        :return: [String]
        """
        if self.ss:
            return self.ss
        else:
            return None

    def add_dd(self, dd):
        """
        Função de que adiciona um SR à lista de SR deste dominio.

        Autor: Pedro Martins.

        :param dd: String
        :return: Void
        """
        self.dd.append(dd)

    def get_dd(self):
        """
        Função que retorna a lista de SR deste dominio.

        Autor: Pedro Martins.

        :return: [String]
        """
        if self.dd:
            return self.dd
        else:
            return None


class Configs:
    """
    Esta classe é responsável por armazenar os dados de um ficheiro de configuração.
    """
    def __init__(self, conf_file):
        """
        Esta classe possui a path para o ficheiro de base de dados "root", para o ficheiro de log universal "all" e
        um dicionárico com todos os domínios do ficheiro de configuração.

        Autor: Miguel Pinto e Pedro Martins.

        :param conf_file: String
        """
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
                domain = auxs.add_end_dot(arr[0]) # Adiciona o "." nas configurações também.

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
                # Transforma num tuplo ao qual se deve conectar.
                addr = str_adress_to_tuple(sp)
                if not self.domains[domain].set_sp(addr):
                    raise Exception(f"Ocorreu mais que uma definição do servidor principal do dominio {domain}")

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

    def is_sp(self, domain):
        """
        Esta função retorna true se o servidor é principal para um determinado dominio.

        Autor: Miguel Pinto e Pedro Martins.

        :param domain: String
        :return: Boolean
        """
        if self.domains[domain].get_sp() is None:
            return True
        else:
            return False

    def get_sp(self, domain):
        """
        Esta função retorna o endereço do servidor principal para um determinado dominio, caso não seja ele próprio.

        Autor: Miguel Pinto e Pedro Martins.

        :param domain: String
        :return: String
        """
        if self.domains[domain].get_sp():
            return self.domains[domain].get_sp()
        else:
            print("!get_sp não obteve nenhum sp!")
            return None

    def get_ss(self, domain):
        """
        Esta função retorna os endereços dos servidores secundários de um determinado dominio, caso não seja ele próprio.

        Autor: Miguel Pinto e Pedro Martins.

        :param domain: String
        :return: [String]
        """
        if self.domains[domain].get_ss():
            return self.domains[domain].get_ss()
        else:
            print("!get_ss não obteve nenhum ss!")
            return None

    def get_dd(self, domain):
        """
        Esta função retorna os endereços dos servidores resolver de um determinado dominio, caso não seja ele próprio.

        Autor: Miguel Pinto e Pedro Martins.

        :param domain: String
        :return: [String]
        """
        if self.domains[domain].get_dd():
            return self.domains[domain].get_dd()
        else:
            print("!get_dd não obteve nenhum dd!")
            return None

    def get_db_path(self, domain):
        """
        Esta função retorna a path para o ficheiro de base de dados de um determinado dominio.

        AUtor: Miguel Pinto e Pedro Martins.

        :param domain: String
        :return: String
        """
        return self.domains[domain].get_db()

    def get_domain_log_file(self, domain):
        """
        Esta função retorna a path para o ficheiro de logs de um determinado dominio.

        Autor: Miguel Pinto e Pedro Martins.

        :param domain: String
        :return: String
        """
        if self.domains[domain].get_log_file():
            return self.domains[domain].get_log_file()
        else:
            #print("!get_db_path não obteve nenhuma referencia a base de dados!")
            return None

    def get_all_log_file(self):
        """
        Esta função retorna a path do ficheiro geral de logs "all"

        Autor Miguel Pinto e Pedro Martins.

        :return: String
        """
        return self.all_log

    # talvez isto fosse verificar as entradas DD se for um SP ou SS, para ver quais os dominios que pode responder. ### TALVEZ A FUNCAO DE BAIXO INUTILIZE ESTA
    def get_domain_names(self):
        """
        Esta função retorna uma lista com todos os nomes dos dominios no ficheiro de configuração.

        Autor: Miguel Pinto e Pedro Martins.

        :return: [String]
        """
        ret = []
        for key in self.domains:
            if key != "all":
                ret.append(key)
        return ret

    def get_all_dd(self):
        """
        Esta função retorna todos os dominios que têm uma entrada DD, ou seja todos os dominios que o servidor pode responder.

        Autor: Pedro Martins.

        :return: [String]
        """
        ret = []
        for key in self.domains:
            if key != "all" and self.domains[key].get_dd():
                ret.append(key)
        return ret

    def get_st_file(self):
        """
        Esta função retorna a path do ficheirod e servidores de topo.

        Autor: Miguel Pinto e Pedro Martins.

        :return: String
        """
        return self.st_file_path

    def get_sp_domains(self):
        """
        Esta função retorna uma lista com os nomes dos dominios que não têm um servidor Principal no DomainInfo.
        O servidor toma o comportamento de SP.

        Autor: Pedro Martins.

        :return: [String]
        """
        result = []
        for value in self.domains.values():
            if value.get_sp() is None:
                dom = value.get_name()
                result.append(dom)
        return result

    # Retorna uma lista com os nomes dos dominios que tem um servidor principal no DomainInfo.
    def get_ss_domains(self):
        """
        Esta função retorna uma lista com os nomes dos dominios que têm um servidor Principal no DomainInfo.
        O servidor toma o comportamento de SS.

        Autor: Pedro Martins.

        :return: [String]
        """
        result = []
        for value in self.domains.values():
            if value.get_sp() is not None:
                dom = value.get_name()
                result.append(dom)
        return result



