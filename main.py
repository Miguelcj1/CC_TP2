import os
import time


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
def main(conf):
    database_path = None
    st_file_path = None
    log_file = "/var/dns/logfile.log"  # path do ficheiro que deve ser criado, caso não seja referido no ficheiro de arranque.
    sp = None
    ss = []
    dd = []

    ## Leitura e análise do ficheiro inicial de configuração.
    fp = open(conf, "r")
    for line in fp:
        arr = line.split()
        if arr[0].startswith("#"):
            pass  # does nothing = nop
        elif arr[1] == "DB":
            database_path = arr[2]
        elif arr[1] == "SP":
            if sp is None:
                sp = arr[2]
            else:
                print("ERRO! Há mais que um servidor primario a ser configurado!!")  # mensagem de erro.
        elif arr[1] == "SS":
            ss.append(arr[2])  # porta incluida na string
        elif arr[1] == "DD":
            dd.append(arr[2])  # porta incluida na string
        elif arr[1] == "ST":
            if arr[0] != "root":
                print("ERRO, pois o parametro de ST deve ser igual a root!!")  # mensagem de erro, pois o parametro deve ser igual a "root".
            elif st_file_path is None:
                st_file_path = arr[2]
            else:
                print("ERRO!! Pois há mais que uma indicação de ST filepaths!")  # mensagem de erro, pois há mais que uma indicação de ST filepaths.

        elif arr[1] == "LG":  # faltam particularidades tendo em conta o domínio, eu acho
            log_file = arr[2]

    fp.close()
    ##
##
    '''
    ## Parsing do ficheiro com a lista de Servidores de Topo que devem ser contactados sempre que necessário.
    f = open(st_file_path, "r")
    for line in f:
        arr = line.split()
        if arr[0].startswith("#"):
            pass  # does nothing = nop
        elif arr[1] == "":
            pass

    f.close()
    ##
    '''

    ## Criação/abertura do ficheiro de log
    fp = open(log_file, "a")
    fp.write("# (TESTE) Ficheiro de log\n")

    fp.close()
    ##

    print(f"Database path: {database_path}")
    print(f"st_file_path: {st_file_path}")
    print(f"Log file: {log_file}")
    print(f"Endereço de SP: {sp}")
    print(f"Endereços de SS: {ss}")
    print(f"Endereços de DD: {dd}")


if __name__ == '__main__':
    main("configuração")

