from multiprocessing.managers import BaseManager
import multiprocessing
import socket
import select
import signal
import threading
import time
import random
import sysv_ipc
import os
import signal

HOST = "localhost"
PORT = 6666

#récupération de la shared_memory
class RemoteManager(BaseManager): pass
RemoteManager.register('get_shared_memory')

m = RemoteManager(address=('localhost', 50000), authkey=b'abracadabra')
m.connect()

shared_memory= m.get_shared_memory()

#récupération des infos nécessaires au début du jeu
couleurs_base = ["rouge", "vert", "bleu", "jaune", "violet"]
couleurs = []
suites_gagnantes = [[1,2,3,4,5],[6,7,8,9,10],[11,12,13,14,15],[16,17,18,19,20],[21,22,23,24,25]]

NUMBER_OF_PLAYERS = int(shared_memory._getvalue()["nb_joueurs"])


for i in range(NUMBER_OF_PLAYERS):
    couleurs.append(couleurs_base[i])

#on donne le nombre de jetons à la shared_memory et l'état du jeu
shared_memory.update({"information_tokens": NUMBER_OF_PLAYERS+3})
shared_memory.update({"game_over": False })
shared_memory.update({"victory": False })

#regler pb de couleurs qui entraine l'utilisation de tuples en reservant des plages de nombres pour chaque couleur
def cards_1player(num_player):
    cartes=[]
    if num_player==1:
    
        for i in range(1,4):
            cartes.append(num_player * 1)
        for i in range(1,3):
            cartes.append(num_player * 2)
            cartes.append(num_player * 3)
            cartes.append(num_player * 4)
        cartes.append(num_player * 5)

    if num_player==2:

        for i in range(1,4):
            cartes.append(6)
        for i in range(1,3):
            cartes.append(7)
            cartes.append(8)
            cartes.append(9)
        cartes.append(10)
    
    if num_player==3:

        for i in range(1,4):
            cartes.append(11)
        for i in range(1,3):
            cartes.append(12)
            cartes.append(13)
            cartes.append(14)
        cartes.append(15)
    
    if num_player==4:

        for i in range(1,4):
            cartes.append(16)
        for i in range(1,3):
            cartes.append(17)
            cartes.append(18)
            cartes.append(19)
        cartes.append(20)
    
    if num_player ==5:

        for i in range(1,4):
            cartes.append(21)
        for i in range(1,3):
            cartes.append(22)
            cartes.append(23)
            cartes.append(24)
        cartes.append(25)    
    


    return cartes

#création et mélange du deck initial
def initialize_deck(nb_players):
    deck_cards = []
    for i in range(1,nb_players+1):
        cartes = cards_1player(i)
        for j in range(len(cartes)):
            deck_cards.append(cartes[j])
    random.shuffle(deck_cards)
    return deck_cards

#test
#deck = initialize_deck(NUMBER_OF_PLAYERS)
#print(f"deck de base {deck}")


#répartition des mains piochées dans le deck initial
def repartition_main(nb_players, deck):
    liste_mains = []
    for i in range (nb_players):
        main = []
        for j in range(5):
            main.append(deck[j])
            deck.pop(j)
        liste_mains.append(main)
        shared_memory.update({f"main{i}" : main})
        
   

#test
#repartition_main(NUMBER_OF_PLAYERS,deck)
#print(f"deck après distrib mains {deck}")

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


#test
#print(recup_couleurs(deck))

#fonction pour rendre une carte à un joueur qui en joue une
def pioche_carte(deck,num_player):
    carte_a_donner = deck[0]
    deck.pop(0)
    shared_memory.update({"deck":deck})
    jeu_player = shared_memory._getvalue()[f"main{num_player}"]
    jeu_player.append(carte_a_donner)
    shared_memory.update({f"main{num_player}":jeu_player})
    

#initialisation des suites en shared memory
def init_suites(NUMBER_OF_PLAYERS):
    for couleur in couleurs:
        shared_memory.update({f"suite {couleur}":[]})

#gestion des sockets
def gestion_interact_socket(HOST, PORT, NUMBER_OF_PLAYERS):
    print("je gère")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setblocking(False)
        server_socket.bind((HOST, PORT))
        server_socket.listen(NUMBER_OF_PLAYERS)

        num_player=0
        

        while num_player<NUMBER_OF_PLAYERS:
            
            try:
                player_socket, address = server_socket.accept()
                player_thread = threading.Thread(target=player_handler, args = (player_socket, address, num_player, NUMBER_OF_PLAYERS,))
                player_thread.start()
                num_player+=1
            except socket.error:
                pass

# fonctions utiles pour gestion des clients par le serveur
def player_handler(player_socket, address, num_player, NUMBER_OF_PLAYERS):
    print("Connected to client:", address)
    data = str(num_player)
    player_socket.sendall(data.encode())

    with player_socket:

            data = ""
            
            # Send other players' hands to the connected player
            if num_player==shared_memory._getvalue()[f"tour"]%NUMBER_OF_PLAYERS:
                data+="c'est à vous de jouer"
            else :
                data+=f"c'est le tour du joueur {(shared_memory._getvalue()['tour'])%NUMBER_OF_PLAYERS}"

            player_socket.sendall(data.encode())
            
            if num_player==shared_memory._getvalue()[f"tour"]%NUMBER_OF_PLAYERS:

                #on récupère dans socket la potentielle action du joueur
                play_action = str(player_socket.recv(1024).decode())
                if "mes" not in play_action:
                    cartejouee= int(play_action[5])
                    suiteconcernee=play_action.split("suite")[1]
                    
                    #récuperation de la main à traiter
                    mainconcernee = shared_memory._getvalue()[f"main{num_player}"]
                    for i in range(len(couleurs)):
                        if couleurs[i]==suiteconcernee:
                            multiplier = i

                    #récupération de la suite à traiter
                    suite = shared_memory._getvalue()[f"suite {suiteconcernee}"]

                    #condition d'erreur
                    erreur =0

                    if suite==[] and mainconcernee[cartejouee-1]!=1+multiplier*5:
                        shared_memory.update({"fuse_tokens":shared_memory._getvalue()["fuse_tokens"]-1})
                        print("Erreur! consommation d'un fuse token")
                        erreur=1
                        if shared_memory._getvalue()["fuse_tokens"] ==0:
                            shared_memory.update({"game_over":True})
                    if suite!=[] and mainconcernee[cartejouee-1]!=suite[len(suite)-1]+1 :
                        shared_memory.update({"fuse_tokens":shared_memory._getvalue()["fuse_tokens"]-1})
                        print("Erreur! consommation d'un fuse token")
                        erreur=1
                        if shared_memory._getvalue()["fuse_tokens"] ==0:
                            shared_memory.update({"game_over":True})

                    #condition d'obtention info token si suite complétée
                    if suite!=[] and mainconcernee[cartejouee-1]==(multiplier+1)*5 and mainconcernee[cartejouee-1]==suite[len(suite)-1]+1:
                        print("Bravo! suite complétée et gain d'un information token")
                        shared_memory.update({"information_tokens":shared_memory._getvalue()["information_tokens"]+1})

                    #traitement local
                    if erreur==0 and len(suite)<5:
                        suite.append(mainconcernee[cartejouee -1])
                        data = "la carte est bien placée"
                    else:
                        data = "la carte est mal placée"

                    player_socket.sendall(data.encode())

                    #reupload suite dans shared_memory
                    shared_memory.update({f"suite {suiteconcernee}":suite})



                    #traitement local de la min
                    mainconcernee.pop(cartejouee-1)

                    #reupload main dans shared memory
                    shared_memory.update({f"main{num_player}":mainconcernee})

                    #reupload final main avec carte piochée
                    if shared_memory._getvalue()["deck"]!=[]:
                        pioche_carte(shared_memory._getvalue()["deck"],num_player)
                    
                    
                    print(shared_memory)


                  

            tour_precedent = 1
            
            
            while shared_memory._getvalue()['game_over'] == False and shared_memory._getvalue()['victory']==False:
                suites_completes=[]
                for i in range(1,len(couleurs)+1):
                    if shared_memory._getvalue()[f"suite {couleurs[i-1]}"]==suites_gagnantes[i-1]:
                        suites_completes.append(i)
                if len(suites_completes)==NUMBER_OF_PLAYERS:
                    shared_memory.update({"victory":True})
                    break
                    print("Bravo! Vous avez gagné")
                    
                    os.kill(shared_memory._getvalue()["mainpid"], signal.SIGKILL)
                    
                   
                    

                if shared_memory._getvalue()['tour'] != tour_precedent: 
                    tour_precedent = shared_memory._getvalue()['tour']
                    
                    data = ""
                        
                    # Send other players' hands to the connected player
                    if num_player==shared_memory._getvalue()[f"tour"]%NUMBER_OF_PLAYERS:
                        data+="c'est à vous de jouer"
                    else :
                        data+=f"c'est le tour du joueur {(shared_memory._getvalue()['tour'])%NUMBER_OF_PLAYERS}"
                    
                    player_socket.sendall(data.encode())

                    if num_player==shared_memory._getvalue()[f"tour"]%NUMBER_OF_PLAYERS:
                        play_action = str(player_socket.recv(1024).decode())
                        if "mes" not in play_action:
                            cartejouee=int(play_action[5])
                            suiteconcernee=play_action.split("suite")[1]
                            #récuperation de la main à traiter
                            mainconcernee = shared_memory._getvalue()[f"main{num_player}"]
                            for i in range(len(couleurs)):
                                if couleurs[i]==suiteconcernee:
                                    multiplier = i

                            
                            #récupération de la suite à traiter
                            suite = shared_memory._getvalue()[f"suite {suiteconcernee}"]

                            #condition pour erreur ou non
                            erreur = 0

                            if suite==[] and mainconcernee[cartejouee-1]!=1+multiplier*5:
                                shared_memory.update({"fuse_tokens":shared_memory._getvalue()["fuse_tokens"]-1})
                                print("Erreur! consommation d'un fuse token")
                                erreur=1
                                if shared_memory._getvalue()["fuse_tokens"] ==0:
                                    shared_memory.update({"game_over":True})
                            if suite!=[] and mainconcernee[cartejouee-1]!=suite[len(suite)-1]+1 :
                                shared_memory.update({"fuse_tokens":shared_memory._getvalue()["fuse_tokens"]-1})
                                print("Erreur! consommation d'un fuse token")
                                erreur=1
                                if shared_memory._getvalue()["fuse_tokens"] ==0:
                                    shared_memory.update({"game_over":True})
                            
                            
                            #traitement local
                            if erreur==0 and len(suite)<5:
                                suite.append(mainconcernee[cartejouee -1])
                                data = "la carte est bien placée"
                                #condition d'obtention info token si suite complétée
                                if mainconcernee[cartejouee-1]==(multiplier+1)*5:
                                    print("Bravo! suite complétée et gain d'un information token")
                                    shared_memory.update({"information_tokens":shared_memory._getvalue()["information_tokens"]+1})
                            else:
                                data = "la carte est mal placée"
                            

                            #reupload suite dans shared_memory
                            shared_memory.update({f"suite {suiteconcernee}":suite})



                            

                            player_socket.sendall(data.encode()) 

                            #traitement local de la min
                            mainconcernee.pop(cartejouee-1)

                            #reupload main dans shared memory
                            shared_memory.update({f"main{num_player}":mainconcernee})

                            #reupload final main avec carte piochée
                            if shared_memory._getvalue()["deck"]!=[]:
                                pioche_carte(shared_memory._getvalue()["deck"],num_player)
                            
                            
                            print(shared_memory)
                        
       
        


                
                    




def main():

    #initialisation du deck, des mains et des suites
    deck = initialize_deck(NUMBER_OF_PLAYERS)

    print(deck)

    repartition_main(NUMBER_OF_PLAYERS,deck)

    init_suites(NUMBER_OF_PLAYERS)
    
    shared_memory.update({"tour":1})

    shared_memory.update({"deck":deck})
    process = multiprocessing.current_process()
    print(process.pid)

    shared_memory.update({"mainpid":process.pid})
    
    #initialisation des interactions game-player
    interaction_game_player = threading.Thread(target = gestion_interact_socket, args = (HOST,PORT, NUMBER_OF_PLAYERS,))
    interaction_game_player.start()
    
    print(shared_memory)
    
    print("début du jeu")

    while not shared_memory._getvalue()["game_over"] :
        

        joueur = shared_memory._getvalue()[f"tour"]%NUMBER_OF_PLAYERS

        print(shared_memory)


        

        #shared_memory.update({"tour":shared_memory._getvalue()["tour"]+1})

        tour_suivant = int(input("tapez 1 pour tour suivant ou 2 pour quitter le jeu\n"))
        if tour_suivant==2:
            shared_memory.update({"game_over":True})
            sysv_ipc.remove_message_queue(shared_memory._getvalue()["mq_id"])
        else : 
            shared_memory.update({"tour":shared_memory._getvalue()[f"tour"]+1})
        
        
    




if __name__ == "__main__":
    main()