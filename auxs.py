
# Verifica se tem um ponto final no fim da string.
def ends_with_dot(string):
    b = False
    if string[-1] == ".":
        b = True
    return b

# Talvez acrescentar isto, nas chaves do dicionário de domains em confs, de maneira a haver uma coerencia nos outros parametros de outras estruturas de dados.
# Funcao que acrescenta um ponto final na string, se ja nao tiver um.
def add_end_dot(string):
    if string[-1] != ".":
        string += "."
    return string

