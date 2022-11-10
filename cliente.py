import socket
import random
import query
import sys


def main():
    if len(sys.argv) > 1:
        string_adress = sys.argv[1] # endereco:porta
    else:
        print("Não foi passado o endereço para onde enviar a query.")
        return

    arr = string_adress.split(":")
    endereco = arr[0]
    porta = 53
    if len(arr) > 1:
        porta = int(arr[1])

    destination = (endereco, porta)


    print("Enviarei as queries para o seguinte endereço: " + str(destination))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    ids = set(range(1,65535)) # talvez enviar a logica de ids para o init_query

    inp = "1" # Inicializo o inp para entrar no seguinte ciclo while.
    while inp != "0":
        print("--------------------")
        print("0: Sair do programa")
        print("1: Enviar query")
        print("a: [DEBUG] AUTOMATIC")
        inp = input("Opção: ")

        if inp == "1":
            #endereco = int(input("Endereço: "))
            #porta = int(input("Porta: "))
            q_dom = input("Query domain: ")
            q_type = input("Query type: ")
            q_flags = input("Query flags: ")
            q_id = random.choice(tuple(ids))

            msg = query.init_send_query(q_id, q_flags, q_dom, q_type)
            s.sendto(msg.encode('utf-8'), destination)

            print("Há espera da resposta..")
            msg, add = s.recvfrom(1024)
            msg = msg.decode('utf-8')
            print(f"Mensagem recebida: \n{msg}\nVinda deste endereço: {add}")

        elif inp == "a" or inp == "A":
            for i in range(1):
                q_id = random.choice(tuple(ids))
                q = query.init_send_query(q_id, "Q", "example.com.", "MX")
                print("Foi enviada a seguinte query: " + q)
                s.sendto(q.encode('utf-8'), destination)
                msg, add = s.recvfrom(1024)
                msg = msg.decode('utf-8')
                print(f"Mensagem recebida: \n{msg}\nVinda deste endereço: {add}")

        elif inp != "0":
            print("Input inválido!")



if __name__ == '__main__':
    main()