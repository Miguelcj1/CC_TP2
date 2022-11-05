import time

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

    def get(self, name, type_of_value):
        all_values = []
        responses_f = None
        n_resp = 0
        arr_resp = []
        n_authorities = 0
        arr_authorities = []
        n_extras = 0
        arr_extras = []
        if self.cache.get(name) is None:
            return None
        if self.cache[name].get(type_of_value) is None:
            return None
        for i in range(len(self.cache[name][type_of_value])):
            r = self.cache[name][type_of_value][i]
            resp = r[0] # obtençao da resposta
            ts = r[1]
            ttl = int (resp.split()[3]) # obtenção do ttl da entrada
            now = time.time()
            if now - ts > ttl:
                del self.cache[name][type_of_value][i]
                continue

            self.cache[name][type_of_value][i] = (resp, now)
            n_resp += 1
            arr_resp.append(resp)

        # Obtenção do resto dos valores (NS, A) se forem necessarios
        # ...

        return ",".join(arr_resp)