import time
from logs import Logs

def line_to_string(arr):
    string = f"{arr[0]} {arr[1]} {arr[2]} {arr[3]} "
    if arr[4] != -1:
        string += str(arr[4])
    return string

class Cache:

    def __init__(self):
        self.COL = 9 # nº de colunas
        self.MAX = 50 # nº maximo de entradas

        #init_line = [Name(0), Type(1), Value(2), TTL(3), Prio(4), origin(5), TimeStamp(6), Index(7), STATUS(8)]
        self.table = [[0, 0, 0, 0, 0, 0, 0, y, "FREE"] for y in range(self.MAX)]


    def search(self, name, type_of_value, ind=0):
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

    # Retorna a resposta ou None, caso nada seja encontrado.
    def get_answers(self, id, name, type_of_value):
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

        # init_line = [Name(0), Type(1), Value(2), TTL(3), Prio(4), origin(5), TimeStamp(6), Index(7), STATUS(8)]
        now = time.time()
        # Obtencao de response_values
        for i in range(self.MAX):
            line = self.table[i]
            # Libertação de espaços
            if line[8] == "VALID" and line[5] == "OTHERS" and now - line[6] > line[3]:
                self.table[i][8] = "FREE"
            if line[8] == "VALID" and line[0] == name and line[1] == type_of_value:
                if line[5] == "FILE":
                    flags.add("A") # significa que obteve a informação pelo servidor primário.
                arr_resp.append(line_to_string(line))
                n_resp += 1
                all_values.append(line[2])
        # CASO NÃO HAJA RESPOSTAS RETORNA NONE.
        if n_resp == 0:
            return None
        responses_f = ",".join(arr_resp)

        # Obtencao de authority_values
        for i in range(self.MAX):
            line = self.table[i]
            # Libertação de espaços
            if line[8] == "VALID" and line[5] == "OTHERS" and time.time() - line[6] > line[3]:
                self.table[i][8] = "FREE"
            if line[8] == "VALID" and line[0] == name and line[1] == "NS":
                if line[5] == "FILE":
                    flags.add("A") # significa que obteve a informação pelo servidor primário.
                arr_authorities.append(line_to_string(line))
                n_authorities += 1
                all_values.append(line[2])
        authorities_f = ",".join(arr_authorities)

        # init_line = [Name(0), Type(1), Value(2), TTL(3), Prio(4), origin(5), TimeStamp(6), Index(7), STATUS(8)]
        # Obtencao de extra_values
        for i in range(self.MAX):
            line = self.table[i]
            # Libertação de espaços ((TALVEZ RETIRAR ESTA VERIFICAÇÃO DE TIMEOUTS))
            if line[8] == "VALID" and line[5] == "OTHERS" and time.time() - line[6] > line[3]:
                self.table[i][8] = "FREE"
            if line[8] == "VALID" and line[0] in all_values and line[1] == "A":
                arr_extras.append(line_to_string(line))
                n_extras += 1
        extras_f = ",".join(arr_extras)

        flags = "+".join(flags)
        string = f"{id},{flags},0,{n_resp},{n_authorities},{n_extras};{name},{type_of_value};"
        data = ";".join((responses_f, authorities_f, extras_f)) + ";"
        return string + data


    # Atualiza a cache com os respetivos valores.
    def update(self, log, name, type_of_value, value, ttl, prio = -1, origin = "OTHERS"):
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

            elif line[8] == "VALID" and origin == "OTHERS" and line[0] == name and line[1] == type_of_value and line[2] == value and line[3] == ttl and line[4] == prio:
                # Atualiza o timestamp do registo que é igual ao que era para ser inserido.
                now = time.time()
                self.table[i][6] = now
                log.ev(now, f"Foi atualizada uma entrada na cache dos seguintes valores: {name} {type_of_value} {value} {ttl} origem:{origin}", name)
                return

        now = time.time()
        self.table[last_free] = [name, type_of_value, value, ttl, prio, origin, now, last_free, "VALID"]
        log.ev(now, f"Foi criada uma entrada na cache dos seguintes valores: {name} {type_of_value} {value} {ttl} origem:{origin}", name)


    # Faz o mesmo que a função anterior (UPDATE) mas faz recebe como argumento uma linha do género do ficheiro de base de dados.
    def update_with_line(self, log, line, origin):
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


    # atualiza, em todas as entradas da cache com Name igual
    # ao domínio passado como argumento, o campo Status para FREE. Quando o temporizador
    # associado à idade da base de dados dum SS relativo a um domínio atinge o valor de SOAEXPIRE,
    # então o SS deve executar esta função para esse domínio. Esta função é exclusiva dos servidores
    # do tipo secundário.
    def free_domain(self, domain):
        for line in self.table:
            if line[0] == domain:
                line[8] = "FREE"


'''
table = Cache()
table.update("example.com.", "MX", "ns1", 30, origin = "OTHERS")
index = table.search("example.com.", "MX")
t=0
'''




'''
# sug: lista de strings que sao a resposta e têm ja toda a informaçao necessaria.
class Cache:

    def __init__(self):
        self.cache = {} # NAME: {TYPE_OF_VALUE: (resposta, timestamp)}

    def add_to_cache(self, name, type_of_value, resposta):
        if self.cache.get(name) is None:
            self.cache[name] = {}
        if self.cache[name].get(type_of_value) is None:
            self.cache[name][type_of_value] = [] # vai ter uma lista do tipo (resposta, timestamp)
        timestamp = time.time()
        self.cache[name][type_of_value].append((resposta, timestamp))


    def search(self, message_id, name, type_of_value):
        all_values = []
        responses_f = ""
        authorities_f = ""
        extras_f = ""
        n_resp = 0
        arr_resp = []
        n_authorities = 0
        arr_authorities = []
        n_extras = 0
        arr_extras = []
        if self.cache.get(name) is None:
            return None

        if self.cache[name].get(type_of_value) is None:
            lista = []
        else:
            lista = self.cache[name].get(type_of_value)

        # Obtenção dos response values
        for i in range(len(lista)):
            r = self.cache[name][type_of_value][i]
            resp = r[0] # obtençao da resposta
            ts = r[1]
            ttl = int (resp.split()[3]) # obtenção do ttl da entrada
            now = time.time()
            # Verificação da validade do timestamp, relativamente ao ttl.
            if now - ts > ttl:
                del self.cache[name][type_of_value][i]
                continue

            self.cache[name][type_of_value][i] = (resp, now)
            n_resp += 1
            arr_resp.append(resp)
        responses_f = ",".join(arr_resp)

        # Obtenção do resto dos valores (NS, A)
        # ...

        data = ";".join((responses_f, authorities_f, extras_f))

        result = ",".join((str(message_id), "", "0", str(n_resp), str(n_authorities), str(n_extras)))
        result += ";" + name  + "," + type_of_value + ";"
        result += data
        return result'''

