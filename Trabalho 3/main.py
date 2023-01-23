# Sistemas Distribuídos

# Atividade 3 - Eleição de Líder: Algoritmo do Valentão

# Franciene Bernardi RA: 761851
# Miriane Cardoso Stefanelli RA: 760933

import string
import time
import socket
import sys
import random
import json

from Mensagem import Mensagem
from threading import Thread

NPROCESS = 5
HOST = '127.0.0.1'
PORT_LIST = [5007, 5008, 5009, 5010, 5011]
TIME_LIMIT = 5 # segundos

# Definindo vetor de mensagens
MSGS = []

# Definindo a mensagem como uma letra aleatória
for i in range(0,20):
    MSGS.append(random.choice(string.ascii_letters))


# Clock de Lamport
clock = 1

my_port = int(sys.argv[1])
my_id = int(sys.argv[2])

election_responses = 0
current_leader = 0
last_message_ACK = False
started_election = False
active = False


def enviar_mensagem(msg, my_id):
    global clock
    global last_message_ACK
    global current_leader
    global started_election
    global election_responses

    msg_type = msg.get_type()

    # print(f'------- TIPO DA MENSAGEM: {msg_type}\n')

    # Setando que recebeu uma mensagem do tipo ACK, ou seja, recebimento da mensagem foi confirmado
    if msg_type == 'ACK':
        last_message_ACK = True

    # Se recebeu a mensagem de OK, significa que encontrou um processo de maior ID
    elif msg_type == 'OK':
        # Colocando o ID das mensagens que responderam em um contador
        election_responses += 1

    # Mensagem do tipo de eleição
    elif msg_type == 'ELECTION':
        reply = criar_resposta('OK', f'OK {my_id}')
        enviar_resposta(reply, msg.get_reply_port())
        
        election_thread = Thread(target=eleicao)
        election_thread.start()

    # Mensagem para anuncionar um novo coordenador
    elif msg_type == 'LEADER_ANNOUNCEMENT':
        started_election = False
        current_leader = msg.get_id()
        print(f'----- Novo líder é: {current_leader} -----\n')

    # Se não for nenhuma das opções acima, sigfica que é uma mensagem normal entre os processos
    else:
        msg_id = msg.get_id()
        msg_clock = msg.get_clock()

        # Envio da confirmação de que recebeu a mensagem
        reply = criar_resposta('ACK', f'ACK do processo {msg_id} com clock {msg_clock}')
        enviar_resposta(reply, msg.get_reply_port())


def eleicao():
    global current_leader
    global started_election
    global election_responses

    if started_election == True:
        return
    else:
        started_election = True

    mensagem = Mensagem(my_id, clock, f'ELECTION {my_id}', "ELECTION", 0)

    # Mandar uma mensagem de ELEIÇÃO para todos os processos com ID maior
    # Os ID são de 0 a 4, porque temos 5 processos
    if my_id < NPROCESS-1:
        for i in range(my_id + 1, NPROCESS):
            enviar(mensagem, PORT_LIST[i])

        # Esperar o tempo determinado para ver se o processo responde
        time.sleep(TIME_LIMIT)

    # Se ninguém responder com OK para a mensagem de eleição enviada
    # Então a lista de resposta estará vazia
    # Isso significa que o processo que enviou a mensagem é o de maior ID
    # Então fazemos desse processo o coordenador
    if election_responses == 0:

        # Enviando mensagem do tipo LEADR ANNOUNCEMENT para anunciar que o coordenador
        announcement_msg = Mensagem(my_id, clock, f'LEADER ANNOUNCEMENT {my_id}', "LEADER_ANNOUNCEMENT", 0)

        # Setando o ID do novo coordenador
        current_leader = my_id
        print(f'----- Novo líder é: {current_leader} -----\n')

        # Enviando a mensagem de anúncio de coordenador para todos os outros processos
        for i in range(NPROCESS):
            if i != my_id:
                enviar(announcement_msg, PORT_LIST[i])

    # Limpando a variavel de respostas
    election_responses = 0


def processar_mensagem(mensagem, my_id):
    # Acessando a variável global para incrementar o clock
    global clock

    # Confirmação que eu recebi o processo
    # print("Recebi a mensagem")
    
    # Atualizar o Clock de Lamport apenas se a mensagem recebida não for a minha própria
    if mensagem.get_id() != my_id:
        msg_clock = mensagem.get_clock()

        if msg_clock > clock:
            clock = msg_clock + 1
        else:
            clock += 1

    print(f'------- TIPO DA MENSAGEM: {mensagem.get_type()}\n')

    print(f'Recebeu mensagem: {mensagem.toJSON()}\n')

    enviar_mensagem(mensagem, my_id)


def receber(my_id, port):
    # Criação do socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Binding do socket a porta
    s.bind(('', port))

    # Criando as threads
    while True:
        data, source = s.recvfrom(1500)
        data = data.decode('utf-8')
        mensagem_json = json.loads(data)
        mensagem = Mensagem(mensagem_json['id'], mensagem_json['clock'], mensagem_json['msg'], mensagem_json['type'], mensagem_json['reply_port'])

        t = Thread(target=processar_mensagem, args=(mensagem, my_id))
        t.start()


def enviar_resposta(mensagem, port):
    # Acessando a variável global para incrementar o clock
    global clock

    # Criação do socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enviar uma mensagem de resposta)
    data = mensagem.toJSON()

    print(f'Enviando resposta para porta {port}: {mensagem.toJSON()}\n\n')
    try:
        s.sendto(data.encode('utf-8'), (HOST, port))
    except OSError as error:
        print(error)
        pass

    # Depois que a mensagem é enviada, incrementamos o clock
    clock += 1


def enviar(mensagem, port):
    # Acessando a variável global para incrementar o clock
    global clock

    # Acessando a variável global da minha porta
    global my_port

    time.sleep(1)

    # Criação do socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enviando a mensagem para os outros processos
    # Setando a porta de respota para a minha porta
    mensagem.set_reply_port(my_port)

    data = mensagem.toJSON()
    print(f'Enviando para a porta {port} a mensagem: {mensagem.toJSON()}\n\n')
    s.sendto(data.encode('utf-8'), (HOST, port))

    # Depois que a mensagem é enviada, incrementamos o clock
    clock += 1


def criar_resposta(msg_type, content):

    msg = Mensagem(my_id, clock, content, msg_type, 0)

    return msg


if __name__ == "__main__":
    print(f"Porta: {my_port}")
    print(f"Iniciando processo: {my_id}")

    # Main thread
    while(True):
        op = input()

        if op == '':
            # Cria thead responśvel por receber as mensagens
            if active == False:
                t = Thread(target=receber, args=(my_id, my_port))
                active = True
                t.start()
                eleicao()

        # Enviando uma mensagem de tipo NORMAL para outro processo
        # Escrever como entrada o número do processo que recebrá a mensagem
        else:
            dest = int(op)
            msg = random.choice(MSGS)
            print("")

            mensagem = Mensagem(my_id, clock, msg, "NORMAL", 0)

            # Enviando uma mensagem e esperando um ACK de confirmação de recebimento
            last_message_ACK = False
            enviar(mensagem, PORT_LIST[dest])
            time.sleep(TIME_LIMIT)

            # Se o destino dessa mensagem for o líder
            # E o líder não responder com ACK, ou seja, não tivemos ACK
            # Isso significa que ele está inativo
            # Então faremos nova eleição
            if last_message_ACK == False and dest == current_leader:
                print("-------- Nova eleição --------\n")

                election_thread = Thread(target=eleicao)
                election_thread.start() 

            print("")