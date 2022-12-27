import time
from logs import Logs


def line_to_string(arr):
    """
    Esta função devolve uma string com os campos (Name(0), Type(1), Value(2), TTL(3), Prio(4) (se for != -1))

    Autor: Pedro Martins.

    :param arr: list(String)
    :return: String
    """
    string = f"{arr[0]} {arr[1]} {arr[2]} {arr[3]}"
    if arr[4] != -1:
        string += f" {arr[4]}"
    return string


class Cache:
    """
    Esta classe é responsável por implementar a cache que será usada por vários componentes do sistema.
    """

    def __init__(self):
        """
        Esta classe possui um array de arrays com tamanho MAX.
        Cada linha desse Array segue o sequinte formato:
        [Name(0), Type(1), Value(2), TTL(3), Prio(4), origin(5), TimeStamp(6), Index(7), STATUS(8)]

        Autor: Miguel Pinto e Pedro Martins.
        """
        self.COL = 9 # nº de colunas
        self.MAX = 100 # nº maximo de entradas # TODO aumentar valor final

        # Inicializa todas as entradas da cache com valores FREE.
        self.table = [[0, 0, 0, 0, 0, 0, 0.0, y, "FREE"] for y in range(self.MAX)]


    #info_line = [Name(0), Type(1), Value(2), TTL(3), Prio(4), origin(5), TimeStamp(6), Index(7), STATUS(8)]
    def search(self, name, type_of_value, ind=0) -> int:
        """
        Esta função recebe o nome e um tipo de valor e procura na cache o primeiro indice que faz match com esses valores.
        Autor: Miguel Pinto e Pedro Martins.
        :param name: String
        :param type_of_value: String
        :param ind: Int (indice pelo qual começa a procura)
        :return: Int
        """
        res = None
        now = time.time()
        for i in range(ind, self.MAX):
            line = self.table[i]
            # Libertação de espaços
            if line[8] == "VALID" and line[5] == "OTHERS" and now - line[6] > line[3]:
                self.table[i][8] = "FREE"
            if line[8] == "VALID" and line[0] == name and line[1] == type_of_value:
                res = i
                break
        return res # retorna o primeiro indice que faz match com (name, type)



    # TODO UNFINISHED BECAUSE OF NEW GET_CLOSEST_NAMES
    def get_closest_adresses_from_cache(self, q_name):
        # Procura por aliases do tipo CNAME em primeiro lugar.
        for i in range(self.MAX):
            line = self.table[i]
            if line[8] == "VALID" and line[1] == "CNAME" and line[0] == q_name:
                q_name = line[2]
                break

        arr_authorities = []
        # init_line = [Name(0), Type(1), Value(2), TTL(3), Prio(4), origin(5), TimeStamp(6), Index(7), STATUS(8)]
        now = time.time()
        # Obtencao de authority_values
        for i in range(self.MAX):
            line = self.table[i]
            if line[8] == "VALID" and q_name.endswith(line[0]) and line[1] == "NS":
                arr_authorities.append(line_to_string(line))
        authorities_f = ",".join(arr_authorities)


    def get_answers(self, log, message_id, q_name, q_type):
        """
        Esta função faz a procura na cache para obter os valores necessários e cria a resposta.
        Autor: Miguel Pinto e Pedro Martins.
        :param log: Logs
        :param message_id: Int
        :param q_name: String
        :param q_type: String
        :return: String
        """

        all_values = []
        n_resp = 0
        arr_resp = []
        n_authorities = 0
        arr_authorities = []
        n_extras = 0
        arr_extras = []
        responses_f = ""
        authorities_f = ""
        extras_f = ""
        flags = set() # conjunto de strings que representam flags, adquiridas ao longo da pesquisa.
        name_exists = False

        # Procura por aliases do tipo CNAME em primeiro lugar.
        for i in range(self.MAX):
            line = self.table[i]
            if line[8] == "VALID" and line[1] == "CNAME" and line[0] == q_name:
                q_name = line[2]
                break

        # init_line = [Name(0), Type(1), Value(2), TTL(3), Prio(4), origin(5), TimeStamp(6), Index(7), STATUS(8)]
        now = time.time()
        # Obtencao de response_values
        for i in range(self.MAX):
            line = self.table[i]
            if line[8] == "VALID" and line[5] == "OTHERS" and now - line[6] > line[3]:
                self.table[i][8] = "FREE"
                #log.ev(now, f"Expirou uma entrada na cache com os seguintes valores: {line[0]} {line[1]} {line[2]} {line[3]}", domain=line[0])

            if line[8] == "VALID" and line[0] == q_name:
                name_exists = True

            if line[8] == "VALID" and line[0] == q_name and line[1] == q_type:
                if line[5] == "FILE" or line[5] == "SP":
                    flags.add("A")
                arr_resp.append(line_to_string(line))
                n_resp += 1
                all_values.append(line[2])

        responses_f = ",".join(arr_resp)

        # Obtencao de authority_values
        for i in range(self.MAX):
            line = self.table[i]
            # Libertação de espaços
            if line[8] == "VALID" and line[5] == "OTHERS" and time.time() - line[6] > line[3]:
                self.table[i][8] = "FREE"
                #log.ev(now, f"Expirou uma entrada na cache com os seguintes valores: {line[0]} {line[1]} {line[2]} {line[3]}",domain=line[0])
            if line[8] == "VALID" and q_name.endswith(line[0]) and line[1] == "NS":
                if line[5] == "FILE" or line[5] == "SP":
                    flags.add("A")
                arr_authorities.append(line_to_string(line))
                n_authorities += 1
                all_values.append(line[2])
        authorities_f = ",".join(arr_authorities)

        # CASO NÃO HAJA RESPOSTAS, não irá procurar extra_values.
        if n_resp == 0 and n_authorities == 0:
            return f"{message_id},A,2,0,0,0;{q_name},{q_type};;"

        # init_line = [Name(0), Type(1), Value(2), TTL(3), Prio(4), origin(5), TimeStamp(6), Index(7), STATUS(8)]
        # Obtencao de extra_values
        for i in range(self.MAX):
            line = self.table[i]
            # Libertação de espaços
            if line[8] == "VALID" and line[5] == "OTHERS" and time.time() - line[6] > line[3]:
                self.table[i][8] = "FREE"
                #log.ev(now, f"Expirou uma entrada na cache com os seguintes valores: {line[0]} {line[1]} {line[2]} {line[3]}", domain=line[0])
            if line[8] == "VALID" and line[0] in all_values and line[1] == "A":
                arr_extras.append(line_to_string(line))
                n_extras += 1
        extras_f = ",".join(arr_extras)

        # Tratamento da resposta final.
        flags = "+".join(flags)
        response_code = 0
        if n_resp == 0 and name_exists:
            response_code = 1
        elif not name_exists:
            response_code = 2

        string = f"{message_id},{flags},{response_code},{n_resp},{n_authorities},{n_extras};{q_name},{q_type};"
        data = ";".join((responses_f, authorities_f, extras_f)) + ";"
        result = string + data
        return result


    def update(self, log, name, type_of_value, value, ttl, prio = -1, origin = "OTHERS"):
        """
        Esta função atualiza a cache com os valores recebidos.
        No caso de os valores ja estarem na cache apena será alterado o timestamp é atualizado.

        Autor: Miguel Pinto e Pedro Martins.

        :param log: Logs
        :param name: String
        :param type_of_value: String
        :param value: String
        :param ttl: Float
        :param prio: Float
        :param origin: String
        :return: Void
        """
        now = time.time()
        last_free = 0
        i = 0
        for i in range(self.MAX):
            line = self.table[i]

            if line[8] == "FREE":
                last_free = i

            if origin != "OTHERS" and line[0] == name and line[1] == type_of_value and line[2] == value and line[3] == ttl and line[4] == prio and line[8] == "VALID":
                # se o registo já existir e o campo Origin da entrada existente for igual a FILE ou SP, ignorasse o pedido de registo.
                return None

            if origin != "OTHERS" and line[8] == "FREE": #Isto acho que nunca acontece.
                now = time.time()
                self.table[i] = [name, type_of_value, value, ttl, prio, origin, now, i, "VALID"]
                log.ev(now, f"Foi criada uma entrada na cache dos seguintes valores: {name} {type_of_value} {value} {ttl} origem:{origin}", name)
                return

            if line[8] == "VALID" and origin == "OTHERS" and line[0] == name and line[1] == type_of_value and line[2] == value and line[3] == ttl and line[4] == prio:
                # Atualiza o timestamp do registo que é igual ao que era para ser inserido.
                now = time.time()
                self.table[i][6] = now
                log.ev(now, f"Foi atualizada uma entrada na cache dos seguintes valores: {name} {type_of_value} {value} {ttl} origem:{origin}", name)
                return

        now = time.time()
        self.table[last_free] = [name, type_of_value, value, ttl, prio, origin, now, last_free, "VALID"]
        log.ev(now, f"Foi criada uma entrada na cache dos seguintes valores: {name} {type_of_value} {value} {ttl} origem:{origin}", name)


    def update_with_line(self, log, line, origin):
        """
        Esta função faz update a cache mas recebe como argumento uma linha do ficheiro de base de dados.
        Autor: Pedro Martins.
        :param log: Logs
        :param line: String
        :param origin: String
        :return: Void
        """
        # Verifica se a linha está vazia ou começa por '#'.
        if not line.strip() or line.startswith("#"):
            return

        arr = line.split()
        name = arr[0]
        type_of_value = arr[1]
        value = arr[2]
        ttl = int(arr[3])
        prio = -1
        if len(arr) > 4:
            prio = int(arr[4])
        self.update(log, name, type_of_value, value, ttl, prio=prio, origin=origin)

    def update_with_query_response(self, log, q_response):
        """
        Esta função recebe uma resposta a uma query e mete os seus valores na cache
        :param log: Objeto Logs
        :param q_response: String que equivale a uma resposta (deve ser a resposta inteira).
        """
        tokens = q_response.split(";")
        response_code = tokens[0].split(",")[2]
        if response_code == 3:
            print("Response code de falha, logo mensagem é indecifravel")
            return
        responses = []

        for token in tokens[2:]:
            rs = token.split(",")
            responses.extend(rs)

        for r in responses:
            self.update_with_line(log, r, "OTHERS")

    def free_domain(self, domain, log):
        """
        Esta função atualiza todas as entradas da cache com o Name igual ao dominio recebido para o status "FREE".
        Esta função é usada por um SS quando o temporizador associado à base de dados atinge o valor de SOARETRY.

        Autor: Pedro Martins.

        :param domain: String
        :param log: Logs
        :return: Void
        """
        for line in self.table:
            if line[0] != 0 and line[0].endswith(domain) and line[5] == "SP":
                #log.ev(time.time(), f"Expirou uma entrada na cache com os seguintes valores: {line[0]} {line[1]} {line[2]} {line[3]}",domain=line[0]) ###
                line[8] = "FREE"


    def get_soa(self, domain, tipo):
        """
        Esta função é usada para obter o valor fornecido em 'tipo' que retornem valores numéricos, de um determinado domínio.

        Autor: Pedro Martins.

        :param domain: String
        :param tipo: String
        :return: Int
        """
        if tipo not in ["SOASERIAL", "SOAREFRESH", "SOARETRY", "SOAEXPIRE"]:
            return None
        ind = self.search(domain, tipo)
        if ind is None:
            return None
        res = self.table[ind][2]
        return int(res)

    def get_soarefresh(self, domain):
        """
        Esta função é usada para obter o valor de soarefresh de um determinado domínio.

        Autor: Pedro Martins.

        :param domain: String
        :return: Int
        """
        ind = self.search(domain, "SOAREFRESH")
        if ind is None:
            return None
        res = self.table[ind][2]
        return int(res)
