import asyncio
from model import Model
from websockets import connect
from pynput import keyboard
from websockets import serve
from websockets.exceptions import ConnectionClosedOK


class MtTextEditApp():
    _model: Model
    _username: str

    def __init__(self, username: str, filetext: str = ""):
        self._model = Model(filetext)
        self._model.add_user(username)
        self._username = username
        self._send_queue = asyncio.Queue()
        self._key_queue = asyncio.Queue()

    def run(self):
        asyncio.run(self._main())

    def connect(self, conn_ip):
        asyncio.run(self._main(True, conn_ip))

    async def send(self, item):
        await self._send_queue.put(item)

    async def parse_key(self, key):
        loop = asyncio.get_event_loop()
        move_keys = {"Key.up", "Key.down", "Key.up", "Key.right", "Key.left"}
        try:
            if len(key) != 1:
                if key not in move_keys:
                    return
                if key == "Key.left":
                    await loop.run_in_executor(self._model.user_pos_shifted_left, self._username)
                    await self.send(
                        f"{self._username} -M {self._model.user_positions[self._username]}")
                if key == "Key.right":
                    await loop.run_in_executor(None, self._model.user_pos_shifted_right, self._username)
                    await self.send(
                        f"{self._username} -M {self._model.user_positions[self._username]}")
            else:
                await loop.run_in_executor(None, self._model.user_wrote_char, self._username, key)
                await self.send(
                    f"{self._username} -E {key} {str(self._model.user_positions[self._username])}")
        except Exception as e:
            print(f"{e}")

    async def _input_handler(self):
        loop = asyncio.get_event_loop()

        def on_press(key):
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key)
            loop.call_soon_threadsafe(self._key_queue.put_nowait, key_str)
        listener = keyboard.Listener(on_press=on_press)
        await asyncio.to_thread(listener.start)
        try:
            while True:
                key = await self._key_queue.get()
                await self.parse_key(key)
        finally:
            await asyncio.to_thread(listener.stop)

    async def _consumer_handler(self, websocket):
        async for message in websocket:
            print(f"{message}")

    async def _producer_handler(self, websocket):
        while True:
            message = await self._send_queue.get()
            try:
                await websocket.send(message)
            except ConnectionClosedOK:
                break

    async def _handler(self, websocket):
        await self.send(f"{self._username} -T ")
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
            await self.send(f"{self._username} -C {self._username}")
            await asyncio.gather(
                self._consumer_handler(client),
                self._producer_handler(client),
                self._input_handler()
            )
