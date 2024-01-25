import multiprocessing
import socket
import pickle

MAX_CONNECTION_THREADS = 5


def game_process(num_players, player_conn):
    # Initialisation du jeu
    # ...

    try:
        while True:
            # Envoi d'informations aux joueurs
            game_info = {'player_hands': [...], 'other_game_state': ...}
            player_conn.send(pickle.dumps(game_info))

            # Réception des actions des joueurs
            player_actions = []
            for _ in range(num_players):
                action = pickle.loads(player_conn.recv())
                player_actions.append(action)

            # Mise à jour de l'état du jeu en fonction des actions des joueurs
            # ...

            # Vérification des conditions de fin du jeu
            if game_over:
                break

    except KeyboardInterrupt:
        print("Game process interrupted.")
    finally:
        # Nettoyage et gestion de la fin du jeu
        # ...

