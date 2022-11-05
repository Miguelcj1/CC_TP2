import socket
import random
import query

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

endereco = '127.0.0.1'
porta = 3334 # porta qualquer acima de 1024


msg = "Adoro Redes :)"
inp = "1"
opt = ""
ids = set(range(1,65535))


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
        s.sendto(msg.encode('utf-8'), (endereco, porta))

        print("Há espera da resposta..")
        msg, add = s.recvfrom(1024)
        msg = msg.decode('utf-8')
        print(f"Mensagem recebida: \n{msg}\nVinda deste endereço: {add}")

    elif inp == "a" or inp == "A":
        for i in range(1):
            q_id = random.choice(tuple(ids))
            q = query.init_send_query(q_id, "Q+A", "example.com.", "MX")
            print("Foi enviada a seguinte query: " + q)
            s.sendto(q.encode('utf-8'), (endereco, porta))
            msg, add = s.recvfrom(1024)
            msg = msg.decode('utf-8')
            print(f"Mensagem recebida: \n{msg}\nVinda deste endereço: {add}")

    elif inp != "0":
        print("Input inválido!")


