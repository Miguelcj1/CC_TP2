import os
import time
import auxs

def email_translator(string):
    """
    Esta função transforma o formato de email que aparece no ficheiro de base de dados para o formato normal.

    Autor: Pedro Martins.

    :param string: String
    :return: String
    """
    arr = string.split("\.")
    last = arr[-1].split(".")[0]
    after = arr[-1].split(".")[1:]
    before = arr[:-1]
    before.append(last)
    before_a = ".".join(before)
    after_a = ".".join(after)
    final = "@".join((before_a, after_a))
    # final[:-1] tira o ultimo ponto final, que vem na string final.
    return final[:-1]


def add_default(name, default):
    """
    Esta função junta as strings name e default com um "." no meio.
    A função é usada para a implementaçao de dominios default onde não é direto a obtenção do dominio.

    Autor: Pedro Martins.

    :param name: String
    :param default: String
    :return: String
    """
    if default is None:
        raise Exception(f"There is no DEFAULT value to add to this name: {name}!")
    return name + "." + default



class Database:

    # Define as diversas variavéis analisadas no ficheiro de base de dados. Também adiciona automaticamente na cache os valores lidos.
    def __init__(self, db_file, cache, origin, log):
        self.DEFAULT = {} # simbolo: valor
        self.SOASP = {} # dominio: nome completo do SP do dominio
        self.SOAADMIN = {} # dominio: endereço de email do admin do dominio
        self.SOASERIAL = {} # dominio: serial_number da sb do dominio
        self.SOAREFRESH = {} # dominio: refresh interval para um SS perguntar ao SP qual o número de série da base de dados dessa zona
        self.SOARETRY = {} # domínio: refresh interval para um SS perguntar ao SP qual o número de série da base de dados dessa zona, apos um timeout.
        self.SOAEXPIRE = {} # dominio: expire time of the ss database replica
        self.NS = {} # dominio: [nome do server, ttl, prio] SUPORTA PRIORIDADES
        self.A = {} # nome do server(abrev): [ip adress, ttl, prio] SUPORTA PRIORIDADES
        self.CNAME = {} # nome do server(abrev): [alias, ttl]
        self.MX = {} # MX dominio: [nome do email_server, ttl, prio] SUPORTA PRIORIDADES
        self.PTR = {} # ip adress: [nome do server, ttl] ((not sure))

        ## Leitura e análise do ficheiro de base de dados.
        try:
            fp = open(db_file, "r")
        except FileNotFoundError:
            raise Exception(f"Database file {db_file} not found!")

        for line in fp:
            try:
                self.add_db_line(line, cache, origin, log)
            except Exception as exc:
                raise Exception(str(exc))


    # Parses an individual line of a DB File for the database and also caches it.
    def add_db_line(self, line, cache, origin, log):

        # Verifica se a linha está vazia ou começa por '#'.
        if not line.strip() or line.startswith("#"):
            return

        arr = line.split() # Divide a string em campos separados por espaço.
        if len(arr) < 3:
            raise Exception(f"A seguinte linha não está de acordo com os pre-requisitos do ficheiro: {line}")

        # Verifica se é usado algum símbolo definido em DEFAULT.
        dom = arr[0]
        name = arr[2]
        simbols = self.DEFAULT.keys()
        for s in simbols:
            if s in dom:
                dom = dom.replace(s, self.DEFAULT[s])
            if s in name:
                name = name.replace(s, self.DEFAULT[s])

        # Verificação da terminação com "." dos nomes completos dos dominios.
        if arr[1] != "DEFAULT" and not auxs.ends_with_dot(dom):
            try:
                dom = add_default(dom, self.DEFAULT.get("@"))
            except Exception as exc:
                raise Exception(str(exc))
        # Verificação da terminação com "." dos nomes completos de e-mail, servidores e hosts (Values).
        if arr[1] not in ("DEFAULT", "A", "SOASERIAL", "SOAREFRESH", "SOARETRY", "SOAEXPIRE") and not auxs.ends_with_dot(name):
            try:
                name = add_default(name, self.DEFAULT.get("@"))
            except Exception as exc:
                raise Exception(str(exc))

        ttl = 0  # Quote: "Quando o TTL não é suportado num determinado tipo, o seu valor deve ser igual a zero."
        if len(arr) > 3:
            ttl = self.DEFAULT.get(arr[3])
            if ttl is None:
                ttl = arr[3]
            try:
                ttl = int(ttl)
            except ValueError:
                raise Exception(f"O campo TTL da seguinte linha não representa um inteiro: {line}")

        prio = -1  # para caso não seja indicada prioridade.
        if len(arr) > 4:
            prio = self.DEFAULT.get(arr[4])
            if prio is None:
                prio = arr[4]
            try:
                prio = int(prio)
            except ValueError:
                raise Exception(f"O campo prioridade da seguinte linha não representa um inteiro: {line}")

        # Adição dos valores à base de dados.
        if arr[1] == "DEFAULT":  ### talvez devesse percorrer o ficheiro, primeiro por DEFAULTs e depois é que percorria tudo o resto, para valores default que estejam depois de uma utilização serem validos.
            if self.DEFAULT.get(dom):
                raise Exception(f"DEFAULT VALUE {dom} ALREADY SET!")
            self.DEFAULT[dom] = name

        elif arr[1] == "SOASP":
            self.SOASP[dom] = (name, ttl)

        elif arr[1] == "SOAADMIN":
            #self.SOAADMIN[dom] = (email_translator(name), ttl)  # faço a tal traduçao de email.
            self.SOAADMIN[dom] = (name, ttl)

        elif arr[1] == "SOASERIAL":
            self.SOASERIAL[dom] = (name, ttl)

        elif arr[1] == "SOAREFRESH":
            self.SOAREFRESH[dom] = (name, ttl)

        elif arr[1] == "SOARETRY":
            self.SOARETRY[dom] = (name, ttl)

        elif arr[1] == "SOAEXPIRE":
            self.SOAEXPIRE[dom] = (name, ttl)

        elif arr[1] == "NS":
            if not self.NS.get(dom):
                self.NS[dom] = []
            self.NS[dom].append((name, ttl, prio))

        elif arr[1] == "A":
            if not self.A.get(dom):
                self.A[dom] = []
            self.A[dom].append((name, ttl, prio))

        elif arr[1] == "CNAME":
            if not self.CNAME.get(dom):
                self.CNAME[dom] = (name, ttl)
            else:
                raise Exception(f"Valor canónico {name} usado mais que uma vez!")

        elif arr[1] == "MX":
            if not self.MX.get(dom):
                self.MX[dom] = []
            self.MX[dom].append((name, ttl, prio))

        elif arr[1] == "PTR":
            if not self.PTR.get(dom):
                self.PTR[dom] = []
            self.PTR[dom].append((name, ttl))

        # Adição dos valores na cache.
        if arr[1] != "DEFAULT": # se o type_of_value == DEFAULT, não é colocado em cache.
            cache.update(log, dom, arr[1], name, ttl, prio=prio, origin=origin)



    def get_DEFAULT(self):
        return self.DEFAULT

    def get_SOASP(self, dom):
        return self.SOASP.get(dom)

    def get_SOAADMIN(self, dom):
        return self.SOAADMIN.get(dom)

    def get_SOASERIAL(self, dom):
        return self.SOASERIAL.get(dom)

    def get_SOAREFRESH(self, dom):
        return self.SOAREFRESH.get(dom)

    def get_SOARETRY(self, dom):
        return self.SOARETRY.get(dom)

    def get_SOAEXPIRE(self, dom):
        return self.SOAEXPIRE.get(dom)

    def get_SOA_(self, param, dom):
        if param == "SOASP":
            return self.SOASP.get(dom)
        elif param == "SOAADMIN":
            return self.SOAADMIN.get(dom)
        elif param == "SOASERIAL":
            return self.SOASERIAL.get(dom)
        elif param == "SOAREFRESH":
            return self.SOAREFRESH.get(dom)
        elif param == "SOARETRY":
            return self.SOARETRY.get(dom)
        elif param == "SOAEXPIRE":
            return self.SOAEXPIRE.get(dom)


    # returns [(name, ttl, prio)]
    def get_NS(self, dom):
        ret = []
        sn = self.NS.get(dom)
        if sn is None:
            return ret
        for n in sn:
            ret.append(n)
        return ret

    # returns [(ip adress, ttl, prio)]
    def get_A(self, name):
        ret = []
        sn = self.A.get(name)
        if sn is None:
            return ret
        for n in sn:
            ret.append(n)
        return ret

    # returns (name, ttl)
    def get_CNAME(self, key):
        return self.CNAME.get(key)

    # returns [(name, ttl, prio)]
    def get_MX(self, name):
        ret = []
        sn = self.MX.get(name)
        if sn is None:
            return ret
        for n in sn:
            ret.append(n)
        return ret

    # returns [(name, ttl)]
    def get_PTR(self, name):
        ret = []
        sn = self.PTR.get(name)
        if sn is None:
            return ret
        for n in sn:
            ret.append(n[0])
        return ret

    def all_db_lines(self):
        ret = [] # array de linhas a retornar
        for k, v in self.SOASP.items():
            arr = [k, "SOASP"]
            f = arr + list(v)
            f = entry_to_line(f)
            ret.append(f)
        for k, v in self.SOAADMIN.items():
            arr = [k, "SOAADMIN"]
            f = arr + list(v)
            f = entry_to_line(f)
            ret.append(f)
        for k, v in self.SOASERIAL.items():
            arr = [k, "SOASERIAL"]
            f = arr + list(v)
            f = entry_to_line(f)
            ret.append(f)
        for k, v in self.SOAREFRESH.items():
            arr = [k, "SOAREFRESH"]
            f = arr + list(v)
            f = entry_to_line(f)
            ret.append(f)
        for k, v in self.SOARETRY.items():
            arr = [k, "SOARETRY"]
            f = arr + list(v)
            f = entry_to_line(f)
            ret.append(f)
        for k, v in self.SOAEXPIRE.items():
            arr = [k, "SOAEXPIRE"]
            f = arr + list(v)
            f = entry_to_line(f)
            ret.append(f)
        for k, v in self.NS.items():
            arr = [k, "NS"]
            for vs in v:
                f = arr + list(vs)
                f = entry_to_line(f)
                ret.append(f)
        for k, v in self.MX.items():
            arr = [k, "MX"]
            for vs in v:
                f = arr + list(vs)
                f = entry_to_line(f)
                ret.append(f)
        for k, v in self.A.items():
            arr = [k, "A"]
            for vs in v:
                f = arr + list(vs)
                f = entry_to_line(f)
                ret.append(f)
        for k, v in self.CNAME.items():
            arr = [k, "CNAME"]
            f = arr + list(v)
            f = entry_to_line(f)
            ret.append(f)
        for k, v in self.PTR.items():
            arr = [k, "PTR"]
            for vs in v:
                f = arr + list(vs)
                f = entry_to_line(f)
                ret.append(f)
        #ret = map(entry_to_line, ret)
        return ret

def entry_to_line(arr): # arr = [name, type_of_value, value, ttl, prio]
    res = ""
    res = f"{arr[0]} {arr[1]} {arr[2]} "
    if len(arr) > 3:
        res += f"{arr[3]} "
    if len(arr) > 4 and str(arr[4]) != "-1":
        res += f"{arr[4]}"
    return res