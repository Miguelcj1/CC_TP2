import os
import auxs

# Nem sei se vai ser util.
def email_translator(string):
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
    if default is None:
        raise Exception(f"There is no DEFAULT value to add to this name: {name}!")
    return name + "." + default


class Database:

    # Define as diversas variavéis analisadas no ficheiro de base de dados.
    def __init__(self, db_file):
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
            arr = line.split()

            # Verifica se a linha está vazia ou começa por '#'.
            if not line.strip() or line.startswith("#"):
                continue  # skips this iteration

            # Verifica se é usado (na primeira palavra) algum símbolo definido em DEFAULT.
            dom = self.DEFAULT.get(arr[0])
            if dom is None:
                dom = arr[0]


            name = self.DEFAULT.get(arr[2])
            if name is None:
                name = arr[2]

            # Verificação da terminação dos nomes com "."
            if arr[1] != "DEFAULT":
                if not auxs.ends_with_dot(dom):
                    try:
                        dom = add_default(dom, self.DEFAULT.get("@"))
                    except Exception as exc:
                        raise Exception(str(exc))
                elif not auxs.ends_with_dot(name):
                    try:
                        name = add_default(name, self.DEFAULT.get("@"))
                    except Exception as exc:
                        raise Exception(str(exc))

            if len(arr) > 3:
                ttl = self.DEFAULT.get(arr[3])
                if ttl is None:
                    ttl = arr[3]
                ttl = int (ttl)
            else:
                ttl = 0 # Quote: "Quando o TTL não é suportado num determinado tipo, o seu valor deve ser igual a zero."

            prio = -1  # para caso n seja indicada prioridade.
            if len(arr) == 5:
                prio = self.DEFAULT.get(arr[4])
                if prio is None:
                    prio = arr[4]
                prio = int(prio)


            if arr[1] == "DEFAULT":
                if self.DEFAULT.get(dom):
                    raise Exception(f"DEFAULT VALUE {dom} ALREADY SET!")
                self.DEFAULT[dom] = name

            elif arr[1] == "SOASP":
                self.SOASP[dom] = name

            elif arr[1] == "SOAADMIN":
                self.SOAADMIN[dom] = email_translator(arr[2]) # faço a tal traduçao de email.

            elif arr[1] == "SOASERIAL":
                self.SOASERIAL[dom] = name

            elif arr[1] == "SOAREFRESH":
                self.SOAREFRESH[dom] = name

            elif arr[1] == "SOARETRY":
                self.SOARETRY[dom] = name

            elif arr[1] == "SOAEXPIRE":
                self.SOAEXPIRE[dom] = name

            elif arr[1] == "NS" and len(arr) > 3: # talvez deva adicionar length restrictions.
                if not self.NS.get(dom):
                    self.NS[dom] = []
                self.NS[dom].append((name, ttl, prio))

            elif arr[1] == "A":
                if not self.A.get(dom):
                    self.A[dom] = []
                self.A[dom].append((name, ttl, prio))

            elif arr[1] == "CNAME":
                if not self.CNAME.get(dom):
                    self.CNAME[dom] = []
                self.CNAME[dom].append((name, ttl))

            elif arr[1] == "MX":
                if not self.MX.get(dom):
                    self.MX[dom] = []
                self.MX[dom].append((name, ttl, prio))

            elif arr[1] == "PTR":
                if not self.PTR.get(dom):
                    self.PTR[dom] = []
                self.PTR[dom].append((name, ttl))

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

    # returns [(name, ttl)]
    def get_CNAME(self, name):
        ret = []
        sn = self.CNAME.get(name)
        if sn is None:
            return ret
        for n in sn:
            ret.append(n)
        return ret

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
