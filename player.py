# player
import socket

 
HOST = "localhost"
PORT = 6666
NUMBER_OF_PLAYERS = 3 #ATTENTION A CA
mains=[]

def Actions_Tour(num_player):
    Action = int(input("Taper 1 pour donner une info et 2 pour jouer une carte"))
    if Action == 1:
        info= str(input("Quelle est l'information à transmettre?"))
        destinataire = int(input("A quel joueur (numéro)?"))
        message = (f"Information : {info} \npour joueur {destinataire}")
        print(message)
        client_socket.sendall(message.encode())
    if Action == 2:
        carte = int(input("Quel est le numéro de la carte que vous voulez jouer?")) 
        suite = str(input("Sur quelle suite (Quelle couleur)?"))   
        message = (f"Carte numéro: {carte} de joueur {num_player} à poser sur suite {suite}")
        client_socket.sendall(message.encode())

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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    data = client_socket.recv(1024)
    mains_recues = data.decode()
    num_player = int(mains_recues[-1])
    mains_recues = mains_recues[:-1]
    #print(f"mains recues {mains_recues}\n")
    print(f"Vous êtes le joueur {num_player}")
    
    numero_main_player = 0
    for i in range (NUMBER_OF_PLAYERS-1):
        

        if num_player != numero_main_player:
            print(f"main joueur {numero_main_player}")
            numero_main_player+=1
        else:
            print(f"main joueur {numero_main_player +1}")
            numero_main_player+=2

        main = mains_recues.split("]")[0] + "]"
        #print(main)
        if i< NUMBER_OF_PLAYERS-2:    
            mains_recues = mains_recues.split("]")[1]
        main = eval(main) #on retransforme le str en liste
        main = recup_couleurs(main) #on remplace les nombres codés par des tuples nombre couleur
        print(main)
        mains.append(main)

    Actions_Tour(num_player)

    
    
    

    
            
        
 