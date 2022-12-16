from socketserver import *
from socket import *
import json
import struct

HOST = '192.168.20.15'
#HOST = '127.0.0.1'

clientsMap = {}
clientNameMap = {}

def build_header(data_len):
    header = {'data_len': data_len}
    return json.dumps(header).encode(encoding='UTF-8')
def send(key, message):
    client = clientsMap[key]
    data_len = len(message.encode(encoding='UTF-8'))
    header = build_header(data_len)
    header_len = len(header)
    struct_bytes = struct.pack('i', header_len)
    try:
        client.send(struct_bytes)
        client.send(header)
        client.send(message.encode(encoding='UTF-8'))
    except :
        return 0
    print("send", message, "to", key)
    return 1

def recv(client_conn):
    try:
        struct_bytes = client_conn.recv(4)
    except ConnectionResetError:
        return "exited".encode(encoding='utf-8')
    header_len = struct.unpack('i', struct_bytes)[0]
    try:
        header_bytes = client_conn.recv(header_len)
    except ConnectionResetError:
        return "exited".encode(encoding='utf-8')
    header = json.loads(header_bytes.decode(encoding='UTF-8'))
    pack_length = header['data_len']
    had_received = 0
    data_body = bytes()  
    while had_received < pack_length:
        try:
            part_body= client_conn.recv(pack_length - had_received)
        except ConnectionResetError:
            return "exited".encode(encoding='utf-8')
        data_body +=  part_body
        part_body_length = len(part_body)
        had_received += part_body_length
    return data_body

class ChatServer(BaseRequestHandler):
    def handle(self) -> None:
        conn = self.request
        clientsMap[self.client_address] = conn
        connecTing = 1
        while True:
            data = recv(conn).decode(encoding="utf-8")
            if data == 'exited':
                if connecTing == 1:
                    print("User {} logout".format(self.client_address))
                    for key, client in clientsMap.items():
                        if key != self.client_address:
                            toSend = {'type':'10', 'msg':'{}离开了聊天室'.format(clientNameMap[self.client_address])}
                            send(key, str(toSend))
                    del clientsMap[self.client_address]
                    del clientNameMap[self.client_address]
                conn.close()
                return
            dataDic = eval(data)
            if dataDic['type'] == '04':
                print("User {} f_logout".format(self.client_address))
                for key, client in clientsMap.items():
                    if key != self.client_address:
                        toSend = {'type':'10', 'msg':'{}离开了聊天室'.format(clientNameMap[self.client_address])}
                        send(key, str(toSend))
                    else :
                        toSend = {'type':'10', 'msg':'你离开了聊天室'}
                        send(key, str(toSend))
                del clientsMap[self.client_address]
                del clientNameMap[self.client_address]
                connecTing = 0
            elif dataDic['type'] == '03':
                if connecTing == 1:
                    print("User {} logout".format(self.client_address))
                    for key, client in clientsMap.items():
                        if key != self.client_address:
                            toSend = {'type':'10', 'msg':'{}离开了聊天室'.format(clientNameMap[self.client_address])}
                            send(key, str(toSend))
                    del clientsMap[self.client_address]
                    del clientNameMap[self.client_address]
                conn.close()
                return
            elif dataDic['type'] == '01':
                clientsMap[self.client_address] = conn
                for key, client in clientsMap.items():
                    if key != self.client_address:
                        toSend = {'type':'10', 'msg':'{}进入了聊天室'.format(dataDic['msg'])}
                        send(key, str(toSend))
                    else:
                        toSend = {'type':'10', 'msg':'欢迎来到聊天室'}
                        send(key, str(toSend))
                clientNameMap[self.client_address] = dataDic['msg']
            elif dataDic['type'] == '02':
                for key, client in clientsMap.items():
                    if key != self.client_address:
                        toSend = {'type':'11', 'msg':dataDic['msg'], 'who':clientNameMap[self.client_address]}
                        send(key, str(toSend))
                    else:
                        toSend = {'type':'11', 'msg':dataDic['msg'], 'who':'我'}
                        send(key, str(toSend))
            print("Recieve {} from {}".format(data, self.client_address))

if __name__ == '__main__':
    server = ThreadingTCPServer((HOST, 11451), ChatServer)
    print('server online!')
    server.serve_forever()
