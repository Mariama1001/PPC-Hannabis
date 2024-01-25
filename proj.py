import multiprocessing
import socket
import select
import signal
import threading
import random



serve = True

# Constants
NUMBER_OF_PLAYERS = 3
NUMBER_OF_COLORS = NUMBER_OF_PLAYERS
HOST = "localhost"
PORT = 6666

# Shared memory
suits_in_construction = multiprocessing.Array('i', [0] * NUMBER_OF_COLORS)
information_tokens = multiprocessing.Value('i', NUMBER_OF_PLAYERS + 3)
fuse_tokens = multiprocessing.Value('i', 3)
Mutex = multiprocessing.Lock()

# Other global variables
game_over = False
current_player = 0

#regler pb de couleurs qui entraine l'utilisation de tuples en reservant des plages de nombres pour chaque couleur
def cards_1player(num_player):
    cartes=[]
    for i in range(1,4):
        cartes.append(num_player * 1)
    for i in range(1,3):
        cartes.append(num_player * 2)
        cartes.append(num_player * 3)
        cartes.append(num_player * 4)
    cartes.append(num_player * 5)
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
        print(f"main{i} = {main}")
        
    return liste_mains

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



#print(recup_couleurs(deck))

#def pioche(deck,num_player):
#    main

#fonction pour fin du jeu propre
def handler(sig, frame):
    global game_over
    if sig == signal.SIGINT:
        game_over = True

# fonctions utiles pour gestion des clients par le serveur
def player_handler(player_socket, address, num_player, all_mains):
    ######lock.aquire()
    with player_socket:
        print("Connected to client:", address)
        data = ""
        # Send other players' hands to the connected player
        for i in range(NUMBER_OF_PLAYERS):
            if i!=num_player:
                data+=(str(all_mains[i]))
        numero_player = str(num_player)
           
        player_socket.sendall(data.encode())
        player_socket.sendall(numero_player.encode())
        data = player_socket.recv(1024)
        infos = data.decode()
        print(infos)        


        print("Disconnecting from player", address)



def gestion_interact_socket(mains):
    print("je gère")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setblocking(False)
        server_socket.bind((HOST, PORT))
        server_socket.listen(NUMBER_OF_PLAYERS)
        num_player = 0
        while num_player<NUMBER_OF_PLAYERS:
            try:
                
                player_socket, address = server_socket.accept()
                player_process = multiprocessing.Process(target=player_handler, args=(player_socket, address, num_player, mains))
                player_process.start()
                num_player+=1
            except socket.error:
                pass

# fonction pour le game process

def game():
    global game_over
    tour = 1
    while not game_over:
        joueur = tour%NUMBER_OF_PLAYERS
        print(f"Nous sommes au tour {tour} et c'est au joueur {joueur} de jouer")
        tour+=1


        

def main():
    #demande nombre de joueurs
    NUMBER_OF_PLAYERS = int(input("Combien de joueurs?"))
    
    #crée et mélange le deck initial
    deck_initial = initialize_deck(NUMBER_OF_PLAYERS)

    #distribue les mains et enlève les cartes concernées du deck initial
    all_mains = repartition_main(NUMBER_OF_PLAYERS, deck_initial)

    interaction_game_player = threading.Thread(target = gestion_interact_socket, args = (all_mains,))
    interaction_game_player.start()

    print("on arrive jusque là")

    game()

    #signal.signal(signal.SIGINT, handler)



if __name__ == "__main__":
    main()


