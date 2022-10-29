

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

class Batabase:

    # Define as diversas variavéis analisadas no ficheiro de base de dados.
    def __init__(self, db_file):
        self.default = None # opcional
        self.name = None
        self.admin = None
        self.serial_number = None
        self.refresh_interval = None
        self.retry_interval = None
        self.ss_expire_db = None



        ## Leitura e análise do ficheiro de base de dados.
        try:
            fp = open(db_file, "r")
        except FileNotFoundError:
            print("Configuration file not found!")
            return None