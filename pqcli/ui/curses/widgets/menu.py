import curses
import typing as T

from ..util import Choice
from .base import Widget


class Menu(Widget):
    def __init__(
        self,
        header: str,
        choices: T.List[Choice],
        scr_height: int,
        scr_width: int,
    ) -> None:
        self.header_lines = header.split("\n")
        self.choices = choices
        self.scr_width = scr_width
        self.scr_height = scr_height

        w = max(map(len, self.header_lines))
        h = len(self.header_lines) + 1 + len(choices)
        self._pad: T.Optional[T.Any] = curses.newpad(h, w)

        for y, line in enumerate(self.header_lines):
            self._pad.move(y, 0)
            self._pad.addstr(line)

        self.active_choice = 0

    def stop(self) -> None:
        del self._pad
        self._pad = None

    def getmaxyx(self) -> T.Tuple[int, int]:
        if not self._pad:
            return (0, 0)
        return self._pad.getmaxyx()

    def next(self) -> None:
        self.active_choice = min(len(self.choices) - 1, self.active_choice + 1)

    def prev(self) -> None:
        self.active_choice = max(0, self.active_choice - 1)

    def keypress(self, key: int) -> None:
        for choice in self.choices:
            if key in choice.keys:
                choice.callback()
                return

        if key in set(map(ord, "jJ")) | {curses.KEY_DOWN}:
            self.next()
            return

        if key in set(map(ord, "kK")) | {curses.KEY_UP}:
            self.prev()
            return

    def render(self) -> None:
        if not self._pad:
            return

        for y, choice in enumerate(self.choices):
            self._pad.move(len(self.header_lines) + 1 + y, 0)
            if y == self.active_choice:
                self._pad.standout()
            self._pad.addstr(choice.desc)
            if y == self.active_choice:
                self._pad.standend()

        self._pad.refresh(
            0,
            0,
            (self.scr_height - self._pad.getmaxyx()[0]) // 2,
            (self.scr_width - self._pad.getmaxyx()[1]) // 2,
            self.scr_height - 1,
            self.scr_width - 1,
        )
