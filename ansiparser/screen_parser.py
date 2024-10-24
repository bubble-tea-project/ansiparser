"""
ansiparser.screen_parser
~~~~~~~~~~~~~~

This module implements the parser that converts sequences into parsed_screen (a collection of InterConverted).
"""

import copy
import re
from collections import deque

from . import converter, re_pattern
from .sequence_parser import SequenceParser
from .sequence_utils import CSIChecker
from .structures import InterConverted , SgrAttributes


def apply_backspace(string: str) -> str:
    """apply backspace '\x08' to a string"""

    result = []
    for char in string:
        if char == '\b' and result:
            result.pop()
        else:
            result.append(char)

    return ''.join(result)


def split_by_ansi(string: str) -> list:
    """Split the string by ANSI escape sequences."""

    results = re.split(re_pattern.ansi_escape, string)

    # Remove empty strings from the results of re.split
    results = list(filter(None, results))

    # If there is only a string, return [string]
    return results


class ScreenParser:

    def __init__(self, screen_height=24, screen_width=80) -> None:

        self.screen_buffer = deque()

        self.current_parsed_screen = []
        self.current_line_index = 0
        self.current_index = 0
        self.current_sgr_attributes = SgrAttributes()

        self.screen_height = screen_height
        self.screen_width = screen_width

        self.last_screen_finish = False

    def __split_by_ed(self, string: str) -> list:
        """Split string by '\x1B[2J'(Erase in Display)."""

        results = re.split(re_pattern.erase_display_clear_screen, string)

        # Remove empty strings from the results of re.split , if pattern at string first
        results = list(filter(None, results))

        # return [string] if there is no ed sequence.
        return results

    def __split_by_newline(self, string: str) -> list:
        """Split string by newline("\r\n", "\n", "\r")"""

        results = re.split("(\r\n|\n|\r)", string)

        # Remove empty strings from the results of re.split , if pattern at string first
        results = list(filter(None, results))

        # return [string] if there is no newline.
        return results

    def __parse_str_only(self, peek: bool) -> str:
        """Parse the string only; remove all ANSI sequences. \n
        If `peek` is True, peek at the current buffer; otherwise, pop elements from the left side of the buffer."""

        if not self.screen_buffer:
            raise IndexError("screen_buffer is empty")

        if peek is True:
            raw_screen = self.screen_buffer[0]
        else:
            raw_screen = self.screen_buffer.popleft()

        csi_checker = CSIChecker()

        parsed_string = ""
        for data in raw_screen:

            splited_sequences = split_by_ansi(data)
            for sequence_str in splited_sequences:

                if not csi_checker.is_csi(sequence_str):
                    parsed_string += sequence_str
        #
        return parsed_string

    def __parse_line(self, raw_line: str, parsed_screen: list) -> tuple[InterConverted, list]:
        """Parse the single line that is split by a newline character."""
        
        csi_checker = CSIChecker()
        sequence_parser = SequenceParser()

        if (self.current_line_index <= len(parsed_screen) - 1):
            # if can access current_parsed_screen, use old
            inter_converted = parsed_screen[self.current_line_index]
        else:
            # or use new
            inter_converted = InterConverted()

        splited_sequences = split_by_ansi(raw_line)
        for sequence_str in splited_sequences:

            # Select Graphic Rendition
            if csi_checker.is_sgr_sequence(sequence_str):
                self.current_sgr_attributes = sequence_parser.parse_sgr(sequence_str, self.current_sgr_attributes)

            # newline
            elif sequence_str in ("\r\n", "\n", "\r"):
                result = sequence_parser.parse_newline(sequence_str, inter_converted,
                                                       self.current_index,
                                                       parsed_screen,
                                                       self.current_line_index)

                inter_converted = result["inter_converted"]
                self.current_index = result["current_index"]
                parsed_screen = result["parsed_screen"]
                self.current_line_index = result["current_line_index"]

            # text
            elif not csi_checker.is_csi(sequence_str):
                inter_converted, self.current_index = sequence_parser.parse_text(sequence_str, inter_converted,
                                                                                 self.current_sgr_attributes,
                                                                                 self.current_index)

            # Erase in Line
            elif csi_checker.is_el_sequence(sequence_str):
                inter_converted = sequence_parser.parse_el(sequence_str, inter_converted, self.current_index)

            # Erase in Display
            elif csi_checker.is_ed_sequence(sequence_str):
                inter_converted, parsed_screen = sequence_parser.parse_ed(sequence_str, inter_converted,
                                                                          self.current_index,
                                                                          parsed_screen,
                                                                          self.current_line_index)

            # Cursor Position
            elif csi_checker.is_cup_sequence(sequence_str):
                result = sequence_parser.parse_cup(sequence_str, inter_converted,
                                                   self.current_index,
                                                   parsed_screen,
                                                   self.current_line_index)

                inter_converted = result["inter_converted"]
                self.current_index = result["current_index"]
                parsed_screen = result["parsed_screen"]
                self.current_line_index = result["current_line_index"]

        #
        return inter_converted, parsed_screen

    def __parse(self, peek: bool) -> list:
        """Remove the current `screen_buffer` and parse, then overwrite `current_parsed_screen`. \n
        If `peek` is True, only peek and parse the current buffer."""

        if not self.screen_buffer:
            raise IndexError("screen_buffer is empty")

        if peek is True:
            raw_screen = self.screen_buffer[0]
            parsed_screen = []
        else:
            raw_screen = self.screen_buffer.popleft()
            parsed_screen = self.current_parsed_screen.copy()

        screen_splited = self.__split_by_newline("".join(raw_screen))
        for raw_line in screen_splited:

            parsed_line, parsed_screen = self.__parse_line(raw_line, parsed_screen)

            max_line_index = len(parsed_screen) - 1
            if self.current_line_index > max_line_index:
                # add new
                parsed_screen.append(parsed_line)
            else:
                # overwrite
                parsed_screen[self.current_line_index] = parsed_line

            # If parsed_screen length exceeds screen_height, scroll (by removing the first line).
            if len(parsed_screen) > self.screen_height:
                parsed_screen.pop(0)
                self.current_line_index -= 1
        #
        return parsed_screen

    def _from_parsed_screen(self, parsed_screen: list) -> None:
        """Initialize from an existing `parsed_screen`."""

        if not (type(parsed_screen) is list and
                parsed_screen and
                type(parsed_screen[0]) is InterConverted):

            raise TypeError()
        else:
            self.current_parsed_screen = parsed_screen

    def _buffer(self) -> None | deque:
        """return screen_buffer"""

        if not self.screen_buffer:
            return None
        else:
            return self.screen_buffer

    def put(self, string: str) -> None:
        """Add new strings to screen_buffer"""

        raw_screens = self.__split_by_ed(apply_backspace(string))
        for raw_screen in raw_screens:

            if raw_screen == "\x1B[2J":
                # Consider 'clear entire screen' as the finish.
                self.last_screen_finish = True
                self.screen_buffer.append([raw_screen])

            elif (self.last_screen_finish or
                  not self.screen_buffer):
                # Create a new screen if the last screen finishes or the buffer is empty.
                self.last_screen_finish = False
                self.screen_buffer.append([raw_screen])

            else:
                # put to last_screen
                last_screen = self.screen_buffer[-1]
                last_screen.extend([raw_screen])

    def parse(self) -> None:
        """Remove the current screen_buffer and parse it."""

        # Parse only when the screen_buffer is not empty.
        if self.screen_buffer:
            self.current_parsed_screen = self.__parse(peek=False)

    def full(self) -> bool:
        """If the current parsed screen is full."""

        if len(self.current_parsed_screen) >= self.screen_height:
            return True
        else:
            return False

    def clear(self) -> None:
        """clear current parsed_screen and index"""

        self.current_parsed_screen = []
        self.current_line_index = 0
        self.current_index = 0

    def finished(self) -> bool:
        """If the current screen buffer is finished (encountered 'clear entire screen')."""

        # has next screen
        if len(self.screen_buffer) >= 2:
            return True
        else:
            return False

    def buffer_empty(self) -> bool:
        """if screen_buffer is empty"""

        if not self.screen_buffer:
            return True
        else:
            return False

    def clear_buffer(self) -> None:
        """clear screen_buffer"""

        self.screen_buffer.clear()

    def clear_old_buffer(self) -> None:
        """Clear the old (finished) screen_buffer."""

        while self.finished():
            self.screen_buffer.popleft()

    def get_parsed_screen(self) -> list:
        """return underlying current `parsed_screen` """
        return copy.deepcopy(self.current_parsed_screen)

    def peek_string(self) -> str:
        """Peek at the current buffer; parse the string only and remove all ANSI sequences."""
        return self.__parse_str_only(peek=True)

    def to_formatted_string(self, peek=False) -> list[str]:
        """Convert the current `parsed_screen` to a formatted string. 
        If `peek` is True, peek at the current buffer and convert it to a formatted string."""

        if peek is True:
            parsed_screen = self.__parse(peek)
        else:
            parsed_screen = self.current_parsed_screen

        parsed_string_list = []
        for parsed_line in parsed_screen:

            parsed_string = converter.to_string(parsed_line)
            parsed_string_list.append(parsed_string)

        return parsed_string_list

    def to_html(self, peek=False) -> list[str]:
        """Convert the current `parsed_screen` to HTML. 
        If `peek` is True, peek at the current buffer and convert it to HTML."""

        if peek is True:
            parsed_screen = self.__parse(peek)
        else:
            parsed_screen = self.current_parsed_screen

        html_lines = []
        for parsed_line in parsed_screen:

            html_tag = converter.to_html(parsed_line)
            html_lines.append(str(html_tag))

        return html_lines
