from asyncio import sleep
import curses
import math
import sys


class View:
    def __init__(self, stdscr, owner_username):
        self._owner_username = owner_username
        self.stdscr = stdscr
        self.offset_y = 0
        self.offset_x = 0

    def _init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def correct_offset_by_owner_pos(self, owner_x, owner_y):
        height, width = self.stdscr.getmaxyx()
        while owner_x - self.offset_x >= width - 1:
            self.offset_x += 1
        while owner_x - self.offset_x < 0:
            self.offset_x -= 1
        while owner_y - self.offset_y >= height - 3:
            self.offset_y += 1
        while owner_y - self.offset_y < 0:
            self.offset_y -= 1

    def _draw_text(self, text_lines, user_positions):
        height, width = self.stdscr.getmaxyx()
        owner_x, owner_y = user_positions[self._owner_username]
        self.correct_offset_by_owner_pos(owner_x, owner_y)
        for y in range(1, height-2):
            line_num = y - 1 + self.offset_y
            if line_num < len(text_lines):
                line = text_lines[line_num][self.offset_x: self.offset_x + width-1]
                self.stdscr.addstr(y, 0, line + " " * (width - len(line)))
            elif y == 1 and len(text_lines) == 0:
                self.stdscr.addstr(y, 0, " "*(width-1))
        for user_x, user_y in user_positions.values():
            if len(text_lines) == 0 or user_y >= len(text_lines) or \
                    len(text_lines) != 0 and user_x >= len(text_lines[user_y]):
                self.stdscr.addstr(
                    user_y + 1 - self.offset_y, user_x - self.offset_x, " ", curses.color_pair(2))
            else:
                self.stdscr.addstr(
                    user_y + 1 - self.offset_y, user_x - self.offset_x, text_lines[user_y][user_x], curses.color_pair(2))
        self.stdscr.refresh()

    def _draw_interface(self):
        title = f" MTTEXT "
        self.stdscr.addstr(0, 0, title, curses.color_pair(2))
