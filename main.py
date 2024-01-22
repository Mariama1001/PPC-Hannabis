import Threading
import multiprocessing
from multiprocessing import Lock
import socket
import select
import time
import signal

# maximum number of threads to handle socket connections with the other processes
MAX_THREADS = 5

# Constants
MIN_PLAYERS = 2
MAX_PLAYERS = 5

# Get the number of players from the user
while True:
    try:
        num_players = int(input(f"Enter the number of players (between {MIN_PLAYERS} and {MAX_PLAYERS}): "))
        if MIN_PLAYERS <= num_players <= MAX_PLAYERS:
            break
        else:
            print(f"Please enter a number between {MIN_PLAYERS} and {MAX_PLAYERS}.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

NUMBER_OF_PLAYERS = num_players
NUMBER_OF_COLORS = NUMBER_OF_PLAYERS

# Shared memory
suits_in_construction = multiprocessing.Array('i', [0] * NUMBER_OF_COLORS)
information_tokens = multiprocessing.Value('i', NUMBER_OF_PLAYERS + 3)
fuse_tokens = multiprocessing.Value('i', 3)
Mutex = Lock()

# Other global variables
game_over = False
current_player = 0

def establish_player_connections(MIN_PLAYERS, MAX_PLAYERS, player_conn):
    # Crée une liste pour stocker les connexions de joueurs
    player_connections = []

    # Crée un serveur socket pour accepter les connexions des joueurs
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('localhost', 12345))
        server_socket.listen()

        print(f"Waiting for players to connect...")

        for _ in range(max_players):
            client_socket, address = server_socket.accept()
            player_connections.append((client_socket, address))

            # Informe le joueur qu'il s'est connecté avec succès
            player_conn.send(f"Player connected: {address}")

            # Si le nombre de joueurs atteint le minimum, arrête d'attendre
            if len(player_connections) >= min_players:
                break

        if min_players <= len(player_connections) <= max_players:
            print("All players connected.")
            player_conn.send(player_connections)
        else:
            print("Error: Incorrect number of players connected.")
            player_conn.send("Error: Incorrect number of players connected.")


def game_logic():
