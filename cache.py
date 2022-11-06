import time



class Cache:

    def __init__(self):
        #w, h = 9, 1024
        col = 9
        MAX = 1024
        self.table = [[0 for x in range(col)] for y in range(MAX)]




table = Cache()

t=0


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

