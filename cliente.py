import socket
import query
import sys

"""
Cliente.py:
    Módulo de implementação dos clientes do sistema DNS.
    Data de criação: 27/10/2022
    Data da última atualização: 13/11/2022
"""

def main():
    """
    Esta função implementa o comportamento dos clientes no sistema DNS.
    A função recebe o endereço para o qual irá enviar querys como argumento.
    O programa também dispõe de um pequena interface gráfica que permite ao utilizador enviar querys de forma mais simples.
    O programa também permite o envio de uma query automática para casos de teste.

    argument adress: String "endereco:porta" ou "endereco"
    argument timeout : Int (Optional) 10
    :return: Void
    """
    if len(sys.argv) < 2:
        print("Não foi passado o endereço para onde enviar a query.")
        return

    string_adress = sys.argv[1] # "endereco:porta" ou "endereco"

    arr = string_adress.split(":")
    endereco = arr[0]
    porta = 5000
    if len(arr) > 1:
        porta = int(arr[1])

    timeout = 10
    if len(sys.argv) > 2:
        if sys.argv[2].isnumeric() and sys.argv[2][0] != "-":
            timeout = int(sys.argv[2])
        else:
            print("Valor de timeout indicado nos parametros é invalido!")
            return


    destination = (endereco, porta)
    print("Enviarei as queries para o seguinte endereço: " + str(destination))
    print(f"O timeout estabelecido é de {timeout} segundos.")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)

    inp = "1"
    while inp != "0":
        print("--------------------")
        print("0: Sair do programa")
        print("1: Enviar query")
        print("a: [DEBUG] AUTOMATIC")
        inp = input("Opção: ")

        if inp == "1":
            q_dom = input("Query domain: ")
            q_type = input("Query type: ")
            #q_flags = input("Query flags: ")
            q_flags = "Q"

            msg = query.init_send_query(q_flags, q_dom, q_type)
            s.sendto(msg.encode('utf-8'), destination)
            print("Foi enviada a seguinte query: " + msg)

            print("Há espera da resposta..")
            try:
                msg, add = s.recvfrom(1024)
                msg = msg.decode('utf-8')
                print(f"Mensagem recebida: \n{msg}\nVinda deste endereço: {add}")
            except socket.timeout:
                print(f"O tempo de espera pela resposta ultrapassou o timeout estabelecido de {timeout} segundos!")
                s.close()
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(timeout)

        elif inp == "a" or inp == "A":
            for i in range(1):
                q = query.init_send_query("Q", "example.com.", "MX")
                print("Foi enviada a seguinte query: " + q)
                s.sendto(q.encode('utf-8'), destination)
                try:
                    msg, add = s.recvfrom(1024)
                    msg = msg.decode('utf-8')
                    print(f"Mensagem recebida: \n{msg}\nVinda deste endereço: {add}")
                except socket.timeout:
                    print(f"O tempo de espera pela resposta ultrapassou o timeout estabelecido de {timeout} segundos!")
                    s.close()
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.settimeout(timeout)

        elif inp != "0":
            print("Input inválido!")

    s.close()




if __name__ == '__main__':
    main()