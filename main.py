import json
import pywintypes
import time
import tkinter
import win32api
import win32con
from threading import Thread
from websocket import WebSocketApp

config = {
    'font': 'Malgun Gothic',
    'fontSize': '20',
    'bold': True,
    # 'position': '+0+0',
    'position': '+0+0',
    'realTopmost': False,
    'alpha': 0.7,

    'foreground-color': 'white',
    'background-color': 'black',
    'transparent-color': None  # '' or None
}

coinList = {
    'KRW-BTC': '비트코인',
    'KRW-VET': '비체인',
    'KRW-XRP': '리플',
    'KRW-MLK': '밀크',
}



class UpbitSocket:
    def __init__(self, label):
        self.label = label

        self.ws = WebSocketApp(
            url="wss://api.upbit.com/websocket/v1",
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=lambda ws, msg: self.on_error(ws, msg),
            on_close=lambda ws: self.on_close(ws),
            on_open=lambda ws: self.on_open(ws))

        self.running = False
        self.coins = {}
        for coin in coinList:
            self.coins[coin] = '0'

    def on_message(self, ws, msg):
        msg = json.loads(msg.decode('utf-8'))

        label.master.wm_attributes("-topmost", True)
        if config['realTopmost']:
            label.master.wm_attributes("-topmost", True)

        if msg['code'] in self.coins:
            self.coins[msg['code']] = format(int(msg['trade_price']), ",")

        buf = ''
        for coin in coinList:
            buf = buf + coinList[coin] + "\t" + self.coins[coin] + '\n'

        buf = buf.rstrip("\n")
        self.label['text'] = buf

        # self.ll.master.wm_attributes("-topmost", False)

    #  self.ll.master.wm_attributes("-topmost", True)

    def on_error(self, ws, msg):
        self.running = False

    def on_close(self, ws):
        self.running = False

    def on_open(self, ws):

        sendData = [
            {'ticket': 'test'},
            {
                'type': 'ticker',
                'codes': [a for a in coinList]
            },
        ]
        ws.send(json.dumps(sendData))



        def check():
            while self.running:
                time.sleep(1)
            self.ws.close()

        th = Thread(target=check, daemon=True)
        th.start()

    def thread(self):
        self.ws.run_forever()

    def start(self):
        th = Thread(target=self.thread, daemon=True)
        th.start()
        self.running = True

    def stop(self):
        self.running = False


if __name__ == "__main__":

    if config['bold']:
        config['bold'] = 'bold'

    # make label
    label = tkinter.Label(text='', font=(config['font'], config['fontSize'], config['bold']),
                          fg=config['foreground-color'], bg=config['background-color'], justify=tkinter.LEFT)
    label.master.overrideredirect(True)
    label.master.geometry(config['position'])
    label.master.lift()
    label.master.wm_attributes("-topmost", True)
    label.master.wm_attributes("-disabled", True)

    if config['transparent-color']:
        label.master.wm_attributes("-transparentcolor", config['transparent-color'])

    label.master.attributes('-alpha', config['alpha'])

    hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))
    exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
    win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)
    label.pack()

    # new upbitSocket
    real = UpbitSocket(label=label)
    real.start()

    # th = Thread(target=UpbitSocket, daemon=True, args=(request, label))
    # th.start()

    label.mainloop()
