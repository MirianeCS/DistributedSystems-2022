# Sistemas Distribuídos

# Atividade 2 - Exclusão Mútua: Ricart & Agrawala

# Franciene Bernardi RA: 761851
# Miriane Cardoso Stefanelli RA: 760933

import time
import socket
import sys
import json
import os

from Recurso import Recurso
from Mensagem import Mensagem
from threading import Thread

# Definindo a porta e o host
GROUP = '127.0.0.1'
PORT_LIST = [5007, 5008, 5009]

# Definindo o número de processos que serão usados
NPROCESS = 3

# Definindo vetor de recursos
RESOURCES = ['A', 'B', 'C']

# Primeiro argumento receberá clock de Lamport
clock = int(sys.argv[1])

# Segundo argumento receberá porta do processo
port_idx = int(sys.argv[2])


def enviar_mensagem(mensagem, resource_list, my_id):
    # Acessando a variável global para incrementar o clock
    global clock
    
    # Criando variável de resposta como vetor vazio
    resposta = {}
    
    # Pegando o recurso na lista de recursos
    resource_name = mensagem.get_resource_name()
    idx = resource_list.index(Recurso(resource_name))
    resource = resource_list[idx]

    # Para imprimir o estado do recurso naquele terminal
    # print('Estado do recurso: ' + resource.state + '\n')

    if mensagem.get_msg_type() == 'REQUEST':
        # Se eu estou acessando o recurso, enviar uma resposta como "PERMISSION DENIED"
        if resource.state == 'using':
            resposta = criar_resposta('PERMISSION DENIED', my_id, resource_name, clock)

        # Se eu quero acessar o recurso, primeiro preciso checar quem está solicitando
        # -> Se eu que solicitei e o meu clock é menor de quem está solicitando, então enviar resposta de "PERMISSION DENIED"
        # -> Se não fui eu que solicitei, enviar uma resposta de "OK"
        elif resource.state == 'requested':
            if resource.req_clock < mensagem.get_clock():
                resposta = criar_resposta('PERMISSION DENIED', my_id, resource_name, clock)

            elif resource.req_clock == mensagem.get_clock():
                if my_id > mensagem.get_id():
                    resposta = criar_resposta('PERMISSION DENIED', my_id, resource_name, clock)

                else:
                    resposta = criar_resposta('OK', my_id, resource_name, clock)

            else:
                resposta = criar_resposta('OK', my_id, resource_name, clock)

        # Se eu não quero acessar o recurso, enviar uma resposta de "OK"
        else:
            resposta = criar_resposta('OK', my_id, resource_name, clock)
            # print('\n', resposta, '\n')
        
        enviar_resposta(resposta, mensagem.get_reply_port())

        # Se eu mandei alguma resposta do tipo "PERMISSION DENIED", colocar o processo que enviou como próximo da fila
        if resposta.get_msg_type() == 'PERMISSION DENIED':
            resource.next_queue.append(mensagem.get_reply_port())

    elif mensagem.get_msg_type() == 'OK':
        resource.n_ok += 1

        # Se eu recebi o "OK" dos outros dois processos, posso então acessar o recurso
        if resource.n_ok == NPROCESS-1:
            acessar_recurso(resource, my_id)


def acessar_recurso(resource, my_id):
    global clock

    print(f'\nAcessando recurso: {resource}\n\n')

    # Mudando estado do recurso para USING
    resource.state = 'using'

    # ---------- Definindo tempo de uso do recurso
    time.sleep(15)
    # time.sleep(40) 

    # Depois que usa o recurso, liberamos o recurso para o próximo processo
    print(f'Liberando recurso: {resource}\n\n')

    # Envia as mensagens de OK para todo processo que está como próximo da fila
    for reply_port in resource.next_queue:
        resposta = criar_resposta('OK', my_id, resource_name, clock)
        enviar_resposta(resposta, reply_port)

    # Resetando atributos para liberar o recurso
    # Resetar o estado
    resource.state = 'unrequested'
    # Resetar o próximo da fila
    resource.next_queue.clear()
    # Resetar o número de OK recebidos para 0
    resource.n_ok = 0


def processar_mensagem(mensagem, resource_list, my_id):
    # Acessando a variável global para incrementar o clock
    global clock

    # Confirmação que eu recebi o processo
    # print("Recebi a mensagem")

    # -------- Descomentar para testar desempate por clock
    time.sleep(5)
    
    # Atualizar o Clock de Lamport apenas se a mensagem recebida não for a minha própria
    if mensagem.get_id() != my_id:
        msg_clock = mensagem.get_clock()

        if msg_clock > clock:
            clock = msg_clock + 1
        else:
            clock += 1

    print(f'Recebeu mensagem: {mensagem.toJSON()}\n')

    enviar_mensagem(mensagem, resource_list, my_id)


def criar_resposta(msg_type, my_id, resource_name, clock):

    mensagem_resposta = Mensagem(my_id, clock, resource_name, msg_type, 0)

    return mensagem_resposta


def receber(resource_list, my_id, port):
    # Criação do socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Binding do socket a porta
    s.bind(('', port))

    # Criando as threads
    while True:
        data, source = s.recvfrom(1500)
        data = data.decode('utf-8')
        mensagem_json = json.loads(data)
        mensagem = Mensagem(mensagem_json['id'], mensagem_json['clock'], mensagem_json['resource_name'], mensagem_json['msg_type'], mensagem_json['reply_port'])

        t = Thread(target=processar_mensagem, args=(mensagem, resource_list, my_id))
        t.start()


def enviar_resposta(mensagem, port):
    # Acessando a variável global para incrementar o clock
    global clock

    # Criação do socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Enviar uma mensagem de resposta
    data = mensagem.toJSON()

    print(f'Enviando resposta para porta {port}: {mensagem.toJSON()}\n\n')

    try:
        s.sendto(data.encode('utf-8'), (GROUP, port))
    except OSError as error:
        print(error)
        pass

    # Depois que a mensagem é enviada, incrementamos o clock
    clock += 1


def enviar(mensagem, port):
    # Acessando a variável global para incrementar o clock
    global clock
    
    # Acessando a variável global do ID da porta
    global port_idx

    # Create UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enviando a mensagem para os outros processos
    mensagem.set_reply_port(PORT_LIST[port_idx])

    data = mensagem.toJSON()
    print(f'Enviando para a porta {port}: {mensagem.toJSON()}\n\n')
    s.sendto(data.encode('utf-8'), (GROUP, port))

    # Depois que a mensagem é enviada, incrementamos o clock
    clock += 1


if __name__ == "__main__":
    # Definindo a nossa lista de recursos com os recursos pré definidos
    resource_list = [Recurso(i) for i in RESOURCES]

    # Definindo ID
    id = os.getpid()

    print(f"Processo de id: {id}\n")

    # Cria thead responsavel por receber as mensagens
    # print("Criando a thread para recebimento de mensagens")

    t = Thread(target=receber, args=(resource_list, id, PORT_LIST[port_idx]))
    t.start()

    # Main thread
    while(True):
        resource_name = input()

        # Mudando o estado do recurso desejado para RESQUESTED e setando o clock
        idx = resource_list.index(Recurso(resource_name))
        resource = resource_list[idx]
        resource.state = 'requested'
        resource.req_clock = clock

        print("")
        print(f'Pedindo permissão para utilizar o recurso {resource_name}')
        print("")

        # Criando mensagem de solicitação
        mensagem = Mensagem(id, clock, resource_name, "REQUEST", 0)

        # Defindo qual a porta que estamos usando
        my_port = PORT_LIST[port_idx]
        
        for i in PORT_LIST:
            if my_port != i:
                time.sleep(3)

                enviar(mensagem, i)
            
        print("")