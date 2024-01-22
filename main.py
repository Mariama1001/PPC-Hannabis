import multiprocessing
import Threading

# Constants
NUMBER_OF_PLAYERS = 3
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
