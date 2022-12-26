
# Verifica se tem um ponto final no fim da string.
def ends_with_dot(string):
    b = False
    if string[-1] == ".":
        b = True
    return b

# Funcao que acrescenta um ponto final na string, se ja nao tiver um.
def add_end_dot(string):
    if string[-1] != ".":
        string += "."
    return string

def str_adress_to_tuple(string, default_port = 5000):
    """
    Esta função recebe um endereço e opcionalmente uma porta e cria um tuplo (endereço, porta).
    Autor: Pedro Martins.
    :param string: String
    :param default_port: Int
    :return: Tuple (endereço, porta)
    """
    arr = string.split(":")
    """
    ## Confirmação que a string tem o formato de um endereço.
    if len(arr[0].split(".")) != 4: # Se for diferente do formato "255.255.255.255"
        return None        
    """
    if len(arr) < 2:
        res = (arr[0], default_port)
        return res
    res = (arr[0], int(arr[1]))
    return res
