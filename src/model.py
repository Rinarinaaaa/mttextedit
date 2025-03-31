from asyncio import sleep
import curses
from view import View


class Model:
    users: set = set()
    user_positions: dict = {}

    def __init__(self, text: str):
        self.text_lines = text.splitlines()
        if text == "":
            self.text_lines = [""]

    async def run_view(self):
        curses.wrapper(self._main_loop)

    def _main_loop(self, stdscr):
        self.view = View(stdscr)
        curses.curs_set(0)
        self.view._init_colors()
        self.view._draw_interface()
        while True:
            self.view._draw_text(self.text_lines, self.user_positions)

    def add_user(self, username):
        self.users.add(username)
        self.user_positions[username] = (0, 0)

    def user_wrote_char(self, username, char):
        user_x, user_y = self.user_positions[username]
        if user_y == len(self.text_lines):
            self.text_lines.append(char)
        else:
            self.text_lines[user_y] = self.text_lines[user_y][user_x:] + \
                char + self.text_lines[user_y][:user_x]
        self.user_pos_shifted_right(username)

    def user_pos_shifted_left(self, username):
        user_x, user_y = self.user_positions[username]
        user_x -= 1
        if user_x < 0:
            user_y -= 1
            if user_y < 0:
                user_y = 0
            user_x = min(len(self.text_lines[user_y]) - 1, 0)
        self.user_positions[username] = (user_x, user_y)

    def user_pos_shifted_right(self, username):
        user_x, user_y = self.user_positions[username]
        user_x += 1
        if user_x > len(self.text_lines[user_y]):
            user_x = 0
            user_y += 1
            if user_y > len(self.text_lines):
                user_y = len(self.text_lines) - 1
                user_x = len(self.text_lines[user_y])
        self.user_positions[username] = (user_x, user_y)
