import Threading
import multiprocessing
from multiprocessing import Lock

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


def game_logic():
