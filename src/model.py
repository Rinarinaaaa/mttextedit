from asyncio import sleep
import curses
from view import View


class Model:
    users: set = set()
    user_positions: dict = {}

    def __init__(self, text: str):
        self.text_lines = text.splitlines()

    async def run_view(self):
        self.view = View()
        curses.wrapper(self.view.run)

    def add_user(self, username):
        self.users.add(username)
        self.user_positions[username] = (0, 0)

    def user_wrote_char(self, username, char):
        user_x, user_y = self.user_positions[username]
        self.text_lines[user_y] = self.text_lines[user_y][:user_x] + \
            char + self.text_lines[user_y][:user_y]
        self.user_pos_shifted_right(username)

    def user_pos_shifted_left(self, username):
        user_x, user_y = self.user_positions[username]
        user_x -= 1
        if user_x < 0:
            user_y -= 1
            if user_y < 0:
                user_y = 0
            user_x = len(self.text_lines[user_y]) - 1
        self.user_positions[username] = (user_x, user_y)

    def user_pos_shifted_right(self, username):
        user_x, user_y = self.user_positions[username]
        user_x += 1
        if user_x >= len(self.text_lines[user_y]):
            user_x = 0
            user_y += 1
            if user_y >= len(self.text_lines):
                user_y = len(self.text_lines) - 1
        self.user_positions[username] = (user_x, user_y)
