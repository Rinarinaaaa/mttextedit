import asyncio
import curses
from model import Model
from websockets import connect
from websockets import serve
from websockets.exceptions import ConnectionClosedOK


class MtTextEditApp():
    _model: Model
    _username: str

    def __init__(self, username: str, filetext: str = ""):
        self._model = Model(filetext, username)
        self._func_by_key_pressed = {
            curses.KEY_LEFT: self._model.user_pos_shifted_left,
            curses.KEY_RIGHT: self._model.user_pos_shifted_right,
            curses.KEY_DOWN: self._model.user_pos_shifted_down,
            curses.KEY_UP: self._model.user_pos_shifted_up,
        }
        self._username = username
        self._send_queue = asyncio.Queue()

    def run(self):
        curses.wrapper(self._main)

    def connect(self, conn_ip):
        curses.wrapper(self._main, True, conn_ip)

    async def send(self, item):
        await self._send_queue.put(item)

    async def _parse_key(self, key):
        if key in self._func_by_key_pressed.keys():
            await self._func_by_key_pressed[key](self._username)
            user_x, user_y = self._model.user_positions[self._username]
            await self.send(
                f"{self._username} -M {str(user_x)} {str(user_y)}")
        else:
            if 32 <= key <= 126:
                key_str = chr(key)
                await self._model.user_wrote_char(self._username, key_str)
                await self.send(
                    f"{self._username} -E " +
                    f"{'\s' if key_str == ' ' else key_str}")

    async def _input_handler(self):
        self.stdscr.nodelay(True)
        while True:
            key = self.stdscr.getch()
            if key != -1:
                await self._parse_key(key)
            await asyncio.sleep(0.01)

    async def _consumer_handler(self, websocket):
        async for message in websocket:
            args = message.split(' ')
            if args[0] not in self._model.users:
                await self._model.add_user(args[0])
            if args[1] == '-T':
                await self._model.text_upload(' '.join(args[2:]))
            if args[1] == '-M':
                await self._model.user_pos_update(args[0],
                                                  int(args[2]), int(args[3]))
            if args[1] == '-E':
                await self._model.user_wrote_char(args[0], args[2] if args[2] != '\s' else ' ')

    async def _producer_handler(self, websocket):
        while True:
            message = await self._send_queue.get()
            try:
                await websocket.send(message)
            except ConnectionClosedOK:
                break

    async def _connection_handler(self, websocket):
        await self.send(f"{self._username} -T {'\n'.join(self._model.text_lines)}")
        await asyncio.gather(
            self._consumer_handler(websocket),
            self._producer_handler(websocket)
        )

    def _main(self, *args, **kwargs):
        asyncio.run(self._async_main(*args, **kwargs))

    async def _async_main(self, stdscr, should_connect=False, conn_ip=''):
        self.stdscr = stdscr
        asyncio.get_event_loop().run_in_executor(None, self._model.run_view, stdscr)
        if not should_connect:
            async with serve(self._connection_handler, "0.0.0.0", 12000) as server:
                await self._input_handler()
        async with connect('ws://' + conn_ip + ':12000') as client:
            await self.send(f"{self._username} -C {self._username}")
            await asyncio.gather(
                self._consumer_handler(client),
                self._producer_handler(client),
                self._input_handler()
            )
