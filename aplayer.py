from multiprocessing.managers import BaseManager
import time 
import socket 
import os
import sysv_ipc
import signal
 
#connexion à la message queue
key = 128
mq = sysv_ipc.MessageQueue(key)

#données utiles pour la socket
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


NUMBER_OF_PLAYERS = shared_memory._getvalue()["nb_joueurs"]



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))

    #reception du numéro du joueur via la socket
    num_player = int(client_socket.recv(1024).decode())
    print(f"Vous êtes le joueur {num_player}")

    #obtention du pid du joueur
    pid = os.getpid()
    shared_memory.update({f"pidjoueur{num_player}":pid})    

    #réception du tour du joueur via la socket
    tourdujoueur = client_socket.recv(1024).decode()
    print(tourdujoueur)


    #récupération et affichage des mains des autres joueurs
    for i in range (NUMBER_OF_PLAYERS):
        if num_player != i:
            print(f"main joueur {i}")
            print(f"{recup_couleurs(shared_memory._getvalue()[f'main{i}'])}")
    
    
    #actions possibles si c'est le tour du joueur
    if num_player==shared_memory._getvalue()[f"tour"]%NUMBER_OF_PLAYERS:
        bonnum=False
        while bonnum==False:
            play_action = int(input("Tapez 1 pour donner une information, 2 pour jouer une carte ou 3 pour quitter le jeu"))
            if play_action==1:
                bonnum=True
            if play_action==2:
                bonnum=True
            if play_action==3:
                bonnum=True
        
        #donner une information
        if play_action==1:
            #consommation d'un information token
            shared_memory.update({"information_tokens":shared_memory._getvalue()["information_tokens"]-1})
            print(f"information token consommé, il en reste {shared_memory._getvalue()['information_tokens']}")

            #récupération des informations à transmettre    
            info = str(input("Quelle information souhaitez vous donner?"))
            destinataire = int(input("numéro du joueur destinataire :"))
            
            #on envoit au game process qu'on choisit de donner une info
            forgame = "message"
            client_socket.sendall(forgame.encode())

            forplayers= f"Information : {info} pour joueur {destinataire}"


            #on envoie autant de fois le message qu'il y a de players qui consomment dans la message queue
            for i in range(NUMBER_OF_PLAYERS):
                mq.send(forplayers.encode())
                
            shared_memory.update({'tour':shared_memory._getvalue()['tour']+1})
        
        #jouer une carte
        elif play_action==2:

            #récupération de la carte et de la suite concernées
            play = int(input("Quelle carte de votre jeu voulez vous jouer? (numéro)"))
            suite = str(input("Sur la suite de couleur : "))
            
            #envoi au game process 
            forgame = f"carte{play} sur suite{suite}"
            client_socket.sendall(forgame.encode())

            #information à transmettre aux joueurs
            forplayers=f"joueur {num_player} joue sa carte {play} sur la suite {suite}"
            for i in range(NUMBER_OF_PLAYERS):
                mq.send(forplayers.encode())
            
            shared_memory.update({'tour':shared_memory._getvalue()['tour']+1})

            #récupération de la validité de notre action traitée par le game process dans la socket
            valid = client_socket.recv(1024)
            print("")
            print(valid.decode())

        #quitter le jeu    
        elif play_action==3:

            #on kill la message queue et tous les process impliqués dans le jeu
            sysv_ipc.remove_message_queue(shared_memory._getvalue()["mq_id"])
            os.kill(shared_memory._getvalue()["mainpid"], signal.SIGKILL)
            for i in range(NUMBER_OF_PLAYERS):
                if num_player == i: 
                    pidcourant=shared_memory._getvalue()[f"pidjoueur{i}"]
                if num_player!=i:
                    os.kill(shared_memory._getvalue()[f"pidjoueur{i}"], signal.SIGKILL)
            
            os.kill(shared_memory._getvalue()["pidsharedmemo"], signal.SIGKILL)

            os.kill(pidcourant, signal.SIGKILL)
    
    tour_precedent =1

    #après le 1er tour : boucle tant que le jeu n'est pas fini
    while shared_memory._getvalue()['game_over'] == False and shared_memory._getvalue()['victory']==False:
        if shared_memory._getvalue()['tour'] != tour_precedent: 
            
            #récupération de l'information ou de la carte jouée par le joueur précédent
            print("")
            message, t = mq.receive()
            print(message.decode())

            
            tour_precedent = shared_memory._getvalue()['tour']


            tourdujoueur = client_socket.recv(1024)
            tourdujoueur = tourdujoueur.decode()
            print(tourdujoueur)

            
            for i in range (NUMBER_OF_PLAYERS):
                if num_player != i:
                    
                    print(f"main joueur {i}")

                    #attente de la récupération de la main complète si deck pas vide (utile pour synchronisation des process)
                    if shared_memory._getvalue()["deck"]!=[]:
                        while len(recup_couleurs(shared_memory._getvalue()[f'main{i}']))!=5:
                            print("récupération de la main")
                    print(f"{recup_couleurs(shared_memory._getvalue()[f'main{i}'])}")
            
            
            #actions possibles si c'est le tour du joueur (même chose qu'au 1er tour (voir lignes 75 à 148))
            if num_player==shared_memory._getvalue()[f"tour"]%NUMBER_OF_PLAYERS:
                
                #on regarde si le jeu n'est pas terminé
                if shared_memory._getvalue()['victory']==True:
                    os.kill(shared_memory._getvalue()["mainpid"], signal.SIGKILL)
                    break
                

                bonnum=False
                while bonnum==False:
                    play_action = int(input("Tapez 1 pour donner une information, 2 pour jouer une carte ou 3 pour quitter le jeu"))
                    if play_action==1:
                        bonnum=True
                    if play_action==2:
                        bonnum=True
                    if play_action==3:
                        bonnum=True
                
                #donner une information
                if play_action==1:
                    shared_memory.update({"information_tokens":shared_memory._getvalue()["information_tokens"]-1})
                    print(f"information token consommé, il en reste {shared_memory._getvalue()['information_tokens']}")
                    
                    info = str(input("Quelle information souhaitez vous donner?")) 
                    destinataire = int(input("numéro du joueur destinataire :"))

                    forgame = "message"
                    client_socket.sendall(forgame.encode())

                    forplayers= f"Information : {info} pour joueur {destinataire}"
                    for i in range(NUMBER_OF_PLAYERS):
                        mq.send(forplayers.encode())

                    shared_memory.update({'tour':shared_memory._getvalue()['tour']+1})

                elif play_action==2:
                    play = int(input("Quelle carte de votre jeu voulez vous jouer? (numéro)"))
                    suite = str(input("Sur la suite de couleur : "))

                    forgame = f"carte{play} sur suite{suite}"
                    client_socket.sendall(forgame.encode())

                    forplayers=f"joueur {num_player} pose sa carte {play} sur la suite {suite}"
                    for i in range(NUMBER_OF_PLAYERS):
                        mq.send(forplayers.encode())

                    shared_memory.update({'tour':shared_memory._getvalue()['tour']+1})

                    print("")
                    valid = client_socket.recv(1024)
                    print(valid.decode())

                elif play_action==3:
                    break

    #affichage de victoire ou défaite en couleur      
    if shared_memory._getvalue()["game_over"]==True:
        print("\033[1;31mPartie perdue")
    
    elif shared_memory._getvalue()["victory"]==True:
        print("\033[1;32mBravo ! Vous avez gagné")

        


    
    #kill de tous les process en lien avec le jeu et de la message queue
    sysv_ipc.remove_message_queue(shared_memory._getvalue()["mq_id"])
    os.kill(shared_memory._getvalue()["mainpid"], signal.SIGKILL)
    for i in range(NUMBER_OF_PLAYERS):
        if num_player!=i:
            os.kill(shared_memory._getvalue()[f"pidjoueur{i}"], signal.SIGKILL)
    os.kill(shared_memory._getvalue()["pidsharedmemo"], signal.SIGKILL)
