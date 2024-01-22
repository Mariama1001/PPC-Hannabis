import random
nb_joueurs = int(input("combien de joueurs?"))

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
deck = initialize_deck(nb_joueurs)
print(f"deck de base {deck}")


#répartition des mains piochées dans le deck initial
def repartition_main(nb_players, deck):
    for i in range (1,nb_players+1):
        main = []
        for j in range(5):
            main.append(deck[j])
            deck.pop(j)
        print(f"main{i} = {main}")

#test
repartition_main(nb_joueurs,deck)
print(f"deck après distrib mains {deck}")

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



print(recup_couleurs(deck))

def pioche(deck,num_player):
    main