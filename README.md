# PPC-Hannabis
#The goal of this programming project is to design and implement a multi-process and multi-thread multiplayer game in Python. The program simulates a game where 2 to 5 players can play simultaneously .

## Features

The program simulates a game of cards called Hannabis. The player processes interact with each other via a message queue end with the game process who organizes the game.
We have three kinds of processes:

game: who implements the game session, manages the deck and keeps track of suits in construction

player: interacts with the user , the game process and other player processes keeping track of and displaying hands and associated information. Interactions with the game process are carried out in a separate thread. 

server shared memory: contains a remote manager to build a shared memory between processes that do not have a parent-child relationship. This shared memory contains: tour, NUMBER_OF_PLAYERS, all the hands of the players, fuse_tokens, information_tokens, state of the game(game_over and victory), the message queue id.
This process also contains the message queue initializer.

## Usage
You can run  the game by launching the different processes in separate terminals:

Firstly : run server_shared_memory.py and choose the number of players

Then : run game.py

Finally : run in separate terminals aplayer.py, you need to run it {number of players} times

Warning:The sysv_ipc module is not included in python. You can download it here:
http://semanchuk.com/philip/sysv_ipc/

Retrieve the compressed tar file of the latest release, uncompress it and issue the following command in the root directory of the release:
login@hostame:~$ python3 setup.py install --user


