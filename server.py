import socket
import threading
import queue
import json  # json.dumps (algunos) paquete json.loads (algunos) desempaquetando
import os
import os.path
import sys


IP = '127.0.0.1'
PORT = 9999     # Puerto
messages = queue.Queue()
users = []   # 0:userName 1:connection
lock = threading.Lock()

def onlines():    # Estadísticas del personal en línea
    online = []
    for i in range(len(users)):
        online.append(users[i][0])
    return online

class ChatServer(threading.Thread):
    global users, que, lock

    def __init__(self):         # Constructor
        threading.Thread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        os.chdir(sys.path[0])
# Aceptar el nombre de usuario del cliente. Si el nombre de usuario está vacío, la IP y el puerto del usuario se utilizan como nombre de usuario. Si el nombre de usuario aparece duplicado, el nombre de usuario agregará el sufijo "2", "3", "4" ...
    def receive(self, conn, addr):             #    
        user = conn.recv(1024)        # nombre de usuario
        user = user.decode()
        if user == 'El usuario no existe':
            user = addr[0] + ':' + str(addr[1])
        tag = 1
        temp = user
        for i in range(len(users)):     #  , agregue números después de los usuarios de revisión
            if users[i][0] == user:
                tag = tag + 1
                user = temp + str(tag)
        users.append((user, conn))
        USERS = onlines()
        self.Load(USERS,addr)
        # Después de obtener el nombre de usuario, continuará aceptando el mensaje del usuario (es decir, el contenido del chat) y cerrará la conexión después del final.
        try:
            while True:
                message = conn.recv(1024)            # Enviar un mensaje
                message = message.decode()
                message = user + ':' + message
                self.Load(message,addr)
            conn.close()
        # Si el usuario está desconectado, elimine al usuario de la lista de usuarios y luego actualice la lista de usuarios.
        except:   
            j = 0            # Conexión de desconexión del usuario
            for man in users:
                if man[0] == user:
                    users.pop(j)       # Eliminar el usuario de salida
                    break
                j = j+1

            USERS = onlines()
            self.Load(USERS,addr)
            conn.close()

# Guarde la dirección y los datos (debe enviarse al cliente) en la cola de mensajes.
    def Load(self, data, addr):
        lock.acquire()
        try:
            messages.put((addr, data))
        finally:
            lock.release()        

    # Después de recibir los datos, el terminal de servicio lo procesará y luego los enviará al cliente. Como se muestra en la figura a continuación, para el contenido de chat, el servidor lo envía directamente al cliente y para la lista de usuarios, se envía por json.dumps.
    def sendData(self): # enviar datos
        while  True:
            if not messages.empty():
                message = messages.get()
                if isinstance(message[1], str):
                    for i in range(len(users)):
                        data = ' ' + message[1]
                        users[i][1].send(data.encode())
                        print(data)
                        print('\n')

                if isinstance(message[1], list):
                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][1].send(data.encode())
                        except:
                            pass

    def run(self):
        self.s.bind((IP,PORT))
        self.s.listen(5)
        q = threading.Thread(target=self.sendData)
        q.start()
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.receive, args=(conn, addr))
            t.start()
        self.s.close()
if __name__ == '__main__':
    cserver = ChatServer()
cserver.start()

