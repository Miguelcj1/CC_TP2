import time
from logs import Logs


def line_to_string(arr):
    """
    Esta função devolve uma string com os campos (Name(0), Type(1), Value(2), TTL(3), Prio(4) (se for != -1))

    Autor: Pedro Martins.

    :param arr: list(String)
    :return: String
    """
    string = f"{arr[0]} {arr[1]} {arr[2]} {arr[3]} "
    if arr[4] != -1:
        string += str(arr[4])
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
        self.MAX = 50 # nº maximo de entradas

        # Inicializa todas as entradas da cache com valores FREE.
        self.table = [[0, 0, 0, 0, 0, 0, 0.0, y, "FREE"] for y in range(self.MAX)]


    #info_line = [Name(0), Type(1), Value(2), TTL(3), Prio(4), origin(5), TimeStamp(6), Index(7), STATUS(8)]
    def search(self, name, type_of_value, ind=0):
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


    #def get_answers(self, log, message_id, q_name, q_type):
    def get_answers(self, confs, log, query, s, address):
        """
        Esta função faz a procura na cache para obter os valores necessários e cria a resposta.

        Autor: Miguel Pinto e Pedro Martins.

        :param confs: Configs
        :param log: Logs
        :param query: String
        :param s: Socket
        :param address: Tuple (endereço, porta)
        :return: Void
        """

        t_start = time.time()

        arr = query.split(";")

        # Header
        header = arr[0]
        h_fields = header.split(",")
        if len(h_fields) != 6:
            # Sintaxe desconhecida da seguinte mensagem no header.
            log.er(time.time(), address, dados=query)
            return
        message_id = h_fields[0]
        flags = h_fields[1]
        # response_code = h_fields[2]
        # num_responses = h_fields[3]
        # num_authorities = h_fields[4]
        # num_extra = h_fields[5]

        # Data: Query Info
        data_qi = arr[1]
        qi_fields = data_qi.split(",")
        if len(qi_fields) != 2:
            # Sintaxe desconhecida da seguinte mensagem no campo Query Info.
            log.er(time.time(), address, dados=query)
            return
        q_name = qi_fields[0]
        q_type = qi_fields[1]

        # Indica nos logs, a receção de uma query relativa a um determinado domínio.
        log.qr(t_start, address, query, domain=q_name)

        if len(arr) < 3:
            log.er(time.time(), address, dados=query, domain=q_name)
            result = f"{message_id},,3,0,0,0;{q_name},{q_type};"  # sendo 3 o código de mensagem não descodificada.
            s.sendto(result.encode("utf-8"), address)
            return

        '''
        # Pelo menos por enquanto esta parte é desnecessaria uma vez que faço isto para queries de perguntas, sem esperar nenhum valor de resposta.
        # Terceira parte da mensagem onde vem informaçao de resposta
        # Data: List of Response, Authorities and Extra Values
        response_qi = arr[2]
        if response_qi:
            resp_fields = response_qi.split(",")
            responses = []
            for r in resp_fields:
                responses.append(r)    
        '''

        # Verifica se deve responder a queries sobre o dominio mencioando, relativo aos DD's.
        respondable_domains = confs.get_all_dd()
        if q_name not in respondable_domains:
            # A query é ignorada se o servidor não for responsável pelo domínio mencionado na query.
            log.ev(time.time(), f"Foi ignorada a seguinte query, uma vez que este servidor não é responsável pelo domínio da query: {query}")
            return

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
                self.table[i][8] = "FREE" # Libertação de espaços
                log.ev(now, f"Expirou uma entrada na cache com os seguintes valores: {line[0]} {line[1]} {line[2]} {line[3]}", dom=line[0])

            if line[8] == "VALID" and line[0] == q_name: ### NAO SEI SE É REALMENTE NECESSARIO ESTA VERIFICAÇAO
                name_exists = True

            if line[8] == "VALID" and line[0] == q_name and line[1] == q_type:
                if line[5] == "FILE" or line[5] == "SP":
                    flags.add("A") # significa que obteve a informação pelo servidor primário.
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
                log.ev(now, f"Expirou uma entrada na cache com os seguintes valores: {line[0]} {line[1]} {line[2]} {line[3]}",dom=line[0])
            if line[8] == "VALID" and line[0] == q_name and line[1] == "NS":
                if line[5] == "FILE":
                    flags.add("A") # significa que obteve a informação pelo servidor primário.
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
                log.ev(now, f"Expirou uma entrada na cache com os seguintes valores: {line[0]} {line[1]} {line[2]} {line[3]}", dom=line[0])
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

        # Envio da mensagem para o respetivo endereço
        ### time.sleep(11) ### DEBUG
        s.sendto(result.encode("utf-8"), address)
        log.rp(time.time(), address, result, domain=q_name)


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

            if origin != "OTHERS" and line[8] == "FREE":
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

    def free_domain(self, domain):
        """
        Esta função atualiza todas as entradas da cache com o Name igual ao dominio recebido para o status "FREE".
        Esta função é usada por um SS quando o temporizador associado à base de dados atinge o valor de SOAEXPIRE.

        Autor: Pedro Martins.

        :param domain: String
        :return: Void
        """
        for line in self.table:
            if line[0] == domain:
                line[8] = "FREE"


    def get_soarefresh(self, domain):
        """
        Esta função é usada para obter o valor de soarefresh de um determinado domínio para ser usado pelo ask_zone_transfer.

        Autor: Pedro Martins.

        :param domain: String
        :return: Void
        """
        ind = self.search(domain, "SOAREFRESH")
        if ind is None:
            return None
        res = self.table[ind][2]
        return int(res)
