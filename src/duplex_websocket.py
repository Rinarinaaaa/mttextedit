import asyncio
import multiprocessing as mp
from model import Model
from websockets import connect
from pynput import keyboard
from websockets import serve
from websockets.exceptions import ConnectionClosedOK


class DuplexWebsocket(mp.Process):
    _model: Model
    _username: str

    def __init__(self, username: str, filetext: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = Model(filetext)
        self._model.add_user(username)
        self._username = username
        self._send_queue = mp.Queue()
        self._key_queue = mp.Queue()

    def run(self):
        asyncio.run(self._main())

    def connect(self, conn_ip):
        asyncio.run(self._main(True, conn_ip))

    def send(self, item):
        self._send_queue.put(item)

    async def _input_handler(self):
        def on_press(key):
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key)
            self._key_queue.put(key_str)
        listener = keyboard.Listener(on_press=on_press)
        await asyncio.to_thread(listener.start)
        try:
            while True:
                key = await asyncio.get_event_loop().run_in_executor(None, self._key_queue.get)
                if len(key) != 1:
                    if key == "Key.left":
                        self._model.user_pos_shifted_left(self._username)
                        self.send(
                            f"{self._username} -M {self._model.user_positions[self._username]}")
                    if key == "Key.right":
                        self._model.user_pos_shifted_right(self._username)
                        self.send(
                            f"{self._username} -M {self._model.user_positions[self._username]}")
                else:
                    self._model.user_wrote_char(self._username, key)
                    self.send(
                        f"{self._username} -E {key} {str(self._model.user_positions[self._username])}")
        finally:
            await asyncio.to_thread(listener.stop)

    async def _consumer_handler(self, websocket):
        async for message in websocket:
            print(f"{message}")

    async def _producer_handler(self, websocket):
        while True:
            message = await asyncio.get_event_loop().run_in_executor(None, self._send_queue.get)
            try:
                await websocket.send(message)
            except ConnectionClosedOK:
                break

    async def _handler(self, websocket):
        await asyncio.gather(
            self._consumer_handler(websocket),
            self._producer_handler(websocket),
            self._input_handler()
        )

    async def _main(self, should_connect=False, conn_ip=''):
        if not should_connect:
            async with serve(self._handler, "0.0.0.0", 12000) as server:
                await asyncio.Future()
        async with connect('ws://' + conn_ip + ':12000') as client:
            self.send(f"{self._username} -C {self._username}")
            await asyncio.gather(
                self._consumer_handler(client),
                self._producer_handler(client),
                self._input_handler()
            )
