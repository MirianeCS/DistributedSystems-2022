# Sistemas Distribuídos

# Atividade 1 - Multicast totalmente ordenado

# Franciene Bernardi RA: 761851
# Miriane Cardoso Stefanelli RA: 760933

import string
import struct
import socket
import sys
import random
import json
import os
import time

from Mensagem import Mensagem
from threading import Thread

# Definindo a porta e o host
PORT = 5007
HOST = '224.1.1.1'

# Definindo o número de processos que serão usados
NPROCESSOS = 3

# Definidno vetor de mensagens
MSGS = []

# Definindo a mensagem como uma letra aleatória
for i in range(0,9):
    MSGS.append(random.choice(string.ascii_letters))

# Clock de Lamport
clock = int(sys.argv[1])


def proccess_mensagem(mensagem, mensagem_fila, my_id):
    global clock
    
    # Só incrementa o clock se não for uma mensagem dele mesmo
    if mensagem.get_id() != my_id:
        mensagem_clock = mensagem.get_clock()

        # Se o clock da mensagem for maior que o valor de clock, então a gente incrementa usando o clock da mensagem
        if mensagem_clock > clock:
            clock = mensagem_clock + 1

        # Senão, incrementa um no clock global
        else:
            clock += 1

    # Verificando se é um ACK
    # Separando as partes do ACK recebido entre seu id e o seu clock
    if mensagem.get_is_ack() == True:
        msg = mensagem.get_msg().split(' ')
        msg_id = int(msg[1])
        mensagem_clock = int(msg[2])
        processo_id = int(msg[3])

        print(f'Recebeu ACK {msg_id} {mensagem_clock} do processo {processo_id}')
        print('')

        for i in mensagem_fila:
            if (i.get_id() == msg_id): 
                if(i.get_clock() == mensagem_clock):
                    i.set_n_ack(i.get_n_ack() + 1)

                    # Se todos os 3 ACKS foram recebidos, então a mensagem foi entregue e podemos remover ela da fila de mensagens
                    if i.get_n_ack() == NPROCESSOS:                        

                        print('\nMensagem confirmada: ' + i.get_msg())
                        print('\n')
                        mensagem_fila.remove(i)
                        
                        # print('\nFila:')
                        # for item in mensagem_fila:
                        #     print('id:' + str(item.get_id()) + '\nclock: ' + str(item.get_clock()) + '\nmsg: ' + item.get_msg())
                        #     print('\n')
                    break

    # Caso não seja um ACK, então ela é uma mensagem
    else:
        print(f'Recebeu mensagem: ')
        print('id:' + str(mensagem.get_id()) + '\nclock: ' + str(mensagem.get_clock()) + '\nmsg: ' + mensagem.get_msg())
        print('\n')

        # Adicionamos a mensagem para a fila com o contador de ACK igual a 0
        mensagem.set_n_ack(0)
        mensagem_fila.append(mensagem)
        
        # Assim que a mensagem é recebida, mandamos um ACK com o mesmo conteúdo
        msg_id = mensagem.get_id()
        mensagem_clock = mensagem.get_clock()
        processo_id = os.getpid()

        ack_mensagem = Mensagem(clock, f'ACK {msg_id} {mensagem_clock} {processo_id}', my_id, True, 0)

        print(f'Enviando ACK {msg_id} {mensagem_clock} do processo {processo_id}\n')
        envia(ack_mensagem)

        # Agora nós adicionamos na fila a mensagem ordenando primeiro pelo clock e depois pelo id
        mensagem_fila.sort(key=lambda x: (x.clock, x.id))


def recebe(mensagem_fila, my_id):
    s = adiciona_socket()

    # Recebo as mensagens recebidas pelo sistema de multicast
    while True:
        data, source = s.recvfrom(1500)
        data = data.decode('utf-8')
        mensagem_json = json.loads(data)
        mensagem = Mensagem(mensagem_json['clock'], mensagem_json['msg'], mensagem_json['id'], mensagem_json['is_ack'], mensagem_json['n_ack'])

        t = Thread(target=proccess_mensagem, args=(mensagem, mensagem_fila, my_id))
        t.start()


def envia(mensagem):
    # Acessando a variável global para incrementar o clock
    global clock

    # Criação do socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Time-to-live - Número máximo de roteadores
    ttl_bin = struct.pack('@i', 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)

    # time.sleep(random.randint(1,9))

    # Enviando a mensagem para os outros processos
    data = mensagem.toJSON()
    print(f'Enviando mensagem: \n id:' + str(mensagem.get_id()) + '\n clock: ' + str(mensagem.get_clock()) + '\n msg: ' + mensagem.get_msg())
    print('\n')
    s.sendto(data.encode('utf-8'), (HOST, PORT))

    # Depois que a mensagem é enviada, incrementamos o clock
    clock += 1


def adiciona_socket():
    # Criação do socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Método para permitir que a porta seja usada por mais de socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Binding do socket a porta
    s.bind(('', PORT))

    host = socket.inet_aton(HOST)
    mreq = struct.pack('4sL', host, socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    return s


if __name__ == "__main__":
    mensagem_fila = []
    id = os.getpid()

    print(f"Processo de id: {id}")
    print('')

    # Criação da thread que receberá a mensagem
    t = Thread(target=recebe, args=(mensagem_fila, id))
    t.start()

    # Thread principal
    while(True):
        input()
        msg = random.choice(MSGS)

        mensagem = Mensagem(clock, msg, id, False, 0)
        envia(mensagem)
