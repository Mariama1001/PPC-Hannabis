from multiprocessing.managers import BaseManager
import sysv_ipc
 
key = 128
 
mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
print(mq.id)
 

#Demande du nombre de joueurs
NUMBER_OF_PLAYERS = int(input("Nombre de joueurs : "))



print(mq.id)
#Utilisation des remote managers pour la shared memory
shared_memory = {"mq_id":mq.id, "nb_joueurs": NUMBER_OF_PLAYERS,"information_tokens" : NUMBER_OF_PLAYERS +3, "fuse_tokens" : 3}
class RemoteManager(BaseManager): pass

RemoteManager.register('get_shared_memory', callable=lambda:shared_memory)

m = RemoteManager(address=('', 50000), authkey=b'abracadabra')
s = m.get_server()
s.serve_forever()





if shared_memory._getvalue()["game_over"]==True:
    mq.remove()

