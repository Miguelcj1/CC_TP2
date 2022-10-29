import os

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

class Database:

    # Define as diversas variavéis analisadas no ficheiro de base de dados.
    def __init__(self, db_file):
        self.default = None # opcional
        self.dom_names = {} # dominio: nome completo do SP do dominio
        self.dom_admins = {} # dominio: endereço de email do admin do dominio
        self.serial_numbers = {} # dominio: serial_number da sb do dominio
        self.refresh_interval = {} # dominio: refresh interval para um SS perguntar ao SP qual o número de série da base de dados dessa zona
        self.retry_interval = {} # dominio: refresh interval para um SS perguntar ao SP qual o número de série da base de dados dessa zona, apos um timeout.
        self.ss_expire_db = {} # dominio: expire time of the ss database replica
        self.server_names = {} # dominio: [nome do server, ttl, prio]
        self.adresses = {} # nome do server(abrev): [ip adress, ttl, prio]
        self.aliases = {} # nome do server(abrev): [alias, ttl]
        self.mail_server = {} # dominio: [nome do email_server, ttl, prio]
        self.ptr = {} # ip adress: [nome do server, ttl] ((not sure))

        ## Leitura e análise do ficheiro de base de dados.
        try:
            fp = open(db_file, "r")
        except FileNotFoundError:
            #print("Database file not found!") ###
            raise Exception("Database file not found!")

        for line in fp:
            arr = line.split()
            # para nao estar a repetir sempre em todos os casos este if, faço-o no inicio.
            if arr[0] == "@" and self.default:
                dom = self.default
            else:
                dom = arr[0]

            # variavéis usuais nos campos.
            name = arr[2]
            ttl = 0
            prio = -1  # para caso n seja indicada prioridade.
            if len(arr) > 3:
                ttl = arr[3]
            if len(arr) == 5:
                prio = arr[4]

            # Verifica se a linha está vazia ou começa por '#'.
            if not line.strip() or arr[0].startswith("#"):
                pass  # does nothing = nop

            elif arr[1] == "DEFAULT" and arr[0] == "@":
                self.default = arr[2]

            elif arr[1] == "SOASP":
                self.dom_names[dom] = arr[2]

            elif arr[1] == "SOAADMIN":
                self.dom_admins[dom] = email_translator(arr[2]) # faço a tal traduçao de email.

            elif arr[1] == "SOASERIAL":
                self.serial_numbers[dom] = arr[2]

            elif arr[1] == "SOAREFRESH":
                self.refresh_interval[dom] = arr[2]

            elif arr[1] == "SOARETRY":
                self.retry_interval[dom] = arr[2]

            elif arr[1] == "SOAEXPIRE":
                self.ss_expire_db[dom] = arr[2]

            elif arr[1] == "NS": # talvez deva adicionar length restrictions.
                if not self.server_names.get(dom):
                    self.server_names[dom] = []
                self.server_names[dom].append((name, ttl, prio))

            elif arr[1] == "A":
                if not self.adresses.get(dom):
                    self.adresses[dom] = []
                self.adresses[dom].append((name, ttl, prio))

            elif arr[1] == "CNAME":
                if not self.aliases.get(dom):
                    self.aliases[dom] = []
                self.aliases[dom].append((name, ttl))

            elif arr[1] == "MX":
                if not self.mail_server.get(dom):
                    self.mail_server[dom] = []
                self.mail_server[dom].append((name, ttl, prio))

            elif arr[1] == "PTR":
                if not self.ptr.get(dom):
                    self.ptr[dom] = []
                self.ptr[dom].append((name, ttl))

    def get_default(self):
        return self.default

    def get_dom_name(self, dom):
        return self.dom_names.get(dom)

    def get_dom_admin(self, dom):
        return self.dom_admins.get(dom)

    def get_serial_number(self, dom):
        return self.serial_numbers.get(dom)

    def get_refresh_interval(self, dom):
        return self.refresh_interval.get(dom)

    def get_retry_interval(self, dom):
        return self.retry_interval.get(dom)

    def get_ss_expire_db(self, dom):
        return self.ss_expire_db.get(dom)

    def get_server_names(self, dom):
        ret = []
        sn = self.server_names.get(dom)
        sn.sort(key=lambda tup: tup[2])
        for n in sn:
            ret.append(n)
        return ret

    def get_adresses(self, name):
        ret = []
        sn = self.adresses.get(name)
        sn.sort(key=lambda tup: tup[2])
        for n in sn:
            ret.append(n)
        return ret

    def get_aliases(self, name):
        ret = []
        sn = self.aliases.get(name)
        for n in sn:
            ret.append(n)
        return ret

    def get_mail_server(self, name):
        ret = []
        sn = self.mail_server.get(name)
        sn.sort(key=lambda tup: tup[2])
        for n in sn:
            ret.append(n)
        return ret

    def get_ptr(self, name):
        ret = []
        sn = self.ptr.get(name)
        for n in sn:
            ret.append(n[0])
        return ret