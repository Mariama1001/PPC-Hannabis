from multiprocessing.managers import BaseManager
import time 
import socket 
import sysv_ipc
 
key = 128
 
mq = sysv_ipc.MessageQueue(key)

HOST = "localhost"
PORT = 6666

#réassocier les nombres des cartes du deck à leur couleur
def recup_couleurs(liste):
    liste_tuples = []
    for carte in liste:
        if 1<=carte<=5:
            couleur = "rouge"
        if 6<=carte<=10:
            couleur = "vert"
        if 11<=carte<=15:
            couleur = "bleu"
        if 16<=carte<=20:
            couleur = "jaune"
        if 21<=carte<=25:
            couleur = "violet"

        if carte%5==0:
            valeur =5
        else:
            valeur = carte%5
        liste_tuples.append([valeur,couleur])
    return liste_tuples

#récupération de la shared_memory
class RemoteManager(BaseManager): pass
RemoteManager.register('get_shared_memory')

m = RemoteManager(address=('localhost', 50000), authkey=b'abracadabra')
m.connect()

shared_memory= m.get_shared_memory()

connexion = False
NUMBER_OF_PLAYERS = shared_memory._getvalue()["nb_joueurs"]
print(shared_memory)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))

    num_player = int(client_socket.recv(1024).decode())
    print(f"Vous êtes le joueur {num_player}")

   
    tourdujoueur = client_socket.recv(1024).decode()
    print(tourdujoueur)


    
    for i in range (NUMBER_OF_PLAYERS):
            

        if num_player != i:
            print(f"main joueur {i}")
            print(f"{recup_couleurs(shared_memory._getvalue()[f'main{i}'])}")
    
    

    if num_player==shared_memory._getvalue()[f"tour"]%NUMBER_OF_PLAYERS:
        play_action = int(input("Tapez 1 pour donner une information ou 2 pour jouer une carte"))
        if play_action==1:
            
            shared_memory.update({"information_tokens":shared_memory._getvalue()["information_tokens"]-1})
            info = str(input("Quelle information souhaitez vous donner?"))
            destinataire = int(input("numéro du joueur destinataire :"))
            forgame = "message"
            forplayers= f"Information : {info} pour joueur {destinataire}"

            print(f"information token consommé, il en reste {shared_memory._getvalue()['information_tokens']}")

            client_socket.sendall(forgame.encode())

            #on envoie autant de fois le message qu'il y a de players qui consomment
            for i in range(NUMBER_OF_PLAYERS):
                
                mq.send(forplayers.encode())
            
            client_socket.sendall(forgame.encode())

            shared_memory.update({'tour':shared_memory._getvalue()['tour']+1})
        elif play_action==2:
            play = int(input("Quelle carte de votre jeu voulez vous jouer? (numéro)"))
            suite = str(input("Sur la suite de couleur : "))
            forgame = f"carte{play} sur suite{suite}"
            forplayers=""
            for i in range(NUMBER_OF_PLAYERS):
                mq.send(forplayers.encode())
            client_socket.sendall(forgame.encode())
            shared_memory.update({'tour':shared_memory._getvalue()['tour']+1})

    
    tour_precedent =1
    while shared_memory._getvalue()['game_over'] == False and shared_memory._getvalue()['victory']==False:
        if shared_memory._getvalue()['tour'] != tour_precedent: 
            
            ##BELEK ICI
            print("")
            #if num_player!=shared_memory._getvalue()[f"tour"]%NUMBER_OF_PLAYERS:
            message, t = mq.receive()
            print(message.decode())
            
            tour_precedent = shared_memory._getvalue()['tour']

            tourdujoueur = client_socket.recv(1024)
            tourdujoueur = tourdujoueur.decode()
            print(tourdujoueur)

      
            for i in range (NUMBER_OF_PLAYERS):
                if num_player != i:
                    print(f"main joueur {i}")

                    print(f"{recup_couleurs(shared_memory._getvalue()[f'main{i}'])}")
            
            

            if num_player==shared_memory._getvalue()[f"tour"]%NUMBER_OF_PLAYERS:
                if shared_memory._getvalue()['victory']==True:
                break
                play_action = int(input("Tapez 1 pour donner une information ou 2 pour jouer une carte"))
                if play_action==1:
                    shared_memory.update({"information_tokens":shared_memory._getvalue()["information_tokens"]-1})
                    info = str(input("Quelle information souhaitez vous donner?"))
                    destinataire = int(input("numéro du joueur destinataire :"))
                    forgame = "message"
                    forplayers= f"Information : {info} pour joueur {destinataire}"

                    print(f"information token consommé, il en reste {shared_memory._getvalue()['information_tokens']}")
                    
                    client_socket.sendall(forgame.encode())

                    for i in range(NUMBER_OF_PLAYERS):
                        
                        mq.send(forplayers.encode())
                    shared_memory.update({'tour':shared_memory._getvalue()['tour']+1})

                elif play_action==2:
                    play = int(input("Quelle carte de votre jeu voulez vous jouer? (numéro)"))
                    suite = str(input("Sur la suite de couleur : "))
                    forgame = f"carte{play} sur suite{suite}"
                    client_socket.sendall(forgame.encode())
                    forplayers=""
                    for i in range(NUMBER_OF_PLAYERS):
                        mq.send(forplayers.encode())
                    shared_memory.update({'tour':shared_memory._getvalue()['tour']+1})

            
    if shared_memory._getvalue()["game_over"]==True:
        print("Partie perdue")
    
    elif shared_memory._getvalue()["victory"]==True:
        print("Bravo ! Vous avez gagné")
        



