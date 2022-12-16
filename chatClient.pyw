from tkinter import *
from socket import *
import threading
import json
import struct
import atexit
from tkinter import filedialog
from keyboard.keyboard import *

WIDTH = 500
HEIGHT = 370

HOST = '192.168.20.15'
#HOST = '127.0.0.1'

def build_header(data_len):
    header = {'data_len': data_len}
    return json.dumps(header).encode(encoding='UTF-8')
def send(client, message):
    data_len = len(message.encode(encoding='UTF-8'))
    header = build_header(data_len)
    header_len = len(header)
    struct_bytes = struct.pack('i', header_len)
    client.send(struct_bytes)
    client.send(header)
    client.send(message.encode(encoding='UTF-8'))

def recv(client_conn):
    struct_bytes = client_conn.recv(4)
    header_len = struct.unpack('i', struct_bytes)[0]
    header_bytes = client_conn.recv(header_len)
    header = json.loads(header_bytes.decode(encoding='UTF-8'))
    pack_length = header['data_len']
    had_received = 0
    data_body = bytes()
    while had_received < pack_length:
        part_body= client_conn.recv(pack_length - had_received)
        data_body +=  part_body
        part_body_length = len(part_body)
        print('part_body_length', part_body_length)
        had_received += part_body_length

    return data_body

class RecvThread(threading.Thread):
    def __init__(self, client:socket):
        threading.Thread.__init__(self)
        self.client = client

    def run(self) -> None:
        while True:
            msg = recv(self.client).decode(encoding='utf-8')
            print("Got msg:", msg)
            dataDic = eval(msg)
            txtInfo.config(state='normal')
            if dataDic['type'] == '10':
                txtInfo.tag_config("SysMsg", foreground = "red")
                txtInfo.insert(END, dataDic['msg'] + '\n', "SysMsg")
            elif dataDic['type'] == '11':
                txtInfo.tag_config("MyMsg", foreground = "blue")
                if(dataDic['who'] == '我'):
                    txtInfo.insert(END, dataDic['who'] + ":\n", "MyMsg")
                    txtInfo.insert(END, dataDic['msg'], "MyMsg")
                else:
                    txtInfo.insert(END, dataDic['who'] + ":\n")
                    txtInfo.insert(END, dataDic['msg'])
            txtInfo.config(state='disable')
            txtInfo.see(END)       

window = Tk()
sw = window.winfo_screenwidth()
sh = window.winfo_screenheight()
window.geometry("{}x{}+{}+{}".format(WIDTH, HEIGHT, (sw - WIDTH) // 2, (sh - HEIGHT) // 2))

#filename = PhotoImage(file = "szc.png")
labelphoto=Label(window)
#labelphoto.pack()

def fynn():
    filename = PhotoImage(file = filedialog.askopenfilename())
    labelphoto.configure(image = filename)
    labelphoto.pack()
    window.mainloop()
    return

fyn = Button(window, text = '昵称', command = fynn)
fyn.place(x = 10, y = 10, width = 50, height = 30)

txtUserName = StringVar()
Entry(window, textvariable=txtUserName).place(x = 70, y = 10, width = 200, height = 30)


tcpClient = socket(AF_INET, SOCK_STREAM)

connecteD = 0
connecTing = 0
def connectServer():
    global connecteD, connecTing
    print("Click Connect")
    if connecteD == 1:
        if connecTing == 1:
            connecTing = 0
            btnConnect.config(text = '连接')
            toSend = {'type':'04'}
            send(tcpClient, str(toSend))
            print("logout")
        else :
            connecTing = 1
            btnConnect.config(text = '断开')
            username = txtUserName.get()
            toSend = {'type':'01', 'msg':username}
            send(tcpClient, str(toSend))
            print("login")
        return
    username = txtUserName.get()
    if username == "":
        print("用户名不得为空")
        return
    elif username == "我":
        print("用户名不得为'我'")
        return
    try:
        tcpClient.connect((HOST, 11451))
    except OSError:
        print("OSE")
        return
    recvThread = RecvThread(tcpClient)
    recvThread.start()
    toSend = {'type':'01', 'msg':username}
    send(tcpClient, str(toSend))
    btnConnect.config(text = '断开')
    connecteD = 1
    connecTing = 1

btnConnect = Button(window, text = '连接', command = connectServer)
btnConnect.place(x = 280, y = 10, width = 50, height = 30)

def dlEndLine(s):
    if len(s) < 2:
        return s
    if s[-2] == '\n' or s[-2] == ' ':
        return dlEndLine(s[:-2] + '\n')
    return s

def sendData():
    if connecTing == 0:
        print("没连上呢")
        return
    toSend = {'type':'02', 'msg':dlEndLine(txtInput.get(1.0, END))}
    if toSend['msg'] == "\n":
        print("消息不得为空")
    else:
        send(tcpClient, str(toSend))
    txtInput.delete(1.0, END)

btnSend = Button(window, text = '发送', command = sendData)
btnSend.place(x = 340, y = 10, width = 50, height = 30)

def clearText():
    txtInfo.config(state='normal')
    txtInfo.delete(1.0, END)
    txtInfo.config(state='disable')

btnClear = Button(window, text = '清除', command = clearText)
btnClear.place(x = 400, y = 10, width = 70, height = 30)

txtInfo = Text(window, state = 'disable')
txtInfo.place(x = 10, y = 50, width = WIDTH - 30, height = 250)

scr = Scrollbar()
scr.pack(side=RIGHT,fill=Y)

txtInfo["yscrollcommand"] = scr.set
scr["command"] = txtInfo.yview

txtInput = Text(window)
txtInput.place(x = 10, y = 310, width = WIDTH - 30, height = 50)

def sdData():
    txtInput.config(state='disable')
    while is_pressed('enter') == True:
        txtInput.config(state='disable')
    txtInput.config(state='normal')
    sendData()

add_hotkey('ctrl+enter',sdData)

window.title("CPP手下的CPP文件编写者们")

@atexit.register
def clean():
    try:
        toSend = {'type':'03'}
        send(tcpClient, str(toSend))
    except :
        exit(0)
    exit(0)

window.protocol('WM_DELETE_WINDOW', clean)
window.mainloop()
