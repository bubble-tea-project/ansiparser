"""
ansiparser.sequence_parser
~~~~~~~~~~~~~~

This module implements the underlying parser that converts sequences to InterConverted.
"""

import copy
import unicodedata

from .sequence_utils import ParametersExtractor
from .structures import InterConverted, WCharPH


def sgr_parameters_to_attributes(parameters: list[int], current_sgr_attributes: dict) -> dict:
    """Convert SGR parameters to attributes."""
    # sgr_attributes = { "style":set() , "background":"" , "foreground":"" }

    for parameter in parameters:

        match parameter:
            case 0:
                # Reset or normal
                current_sgr_attributes["style"].clear()
                current_sgr_attributes["background"] = ""
                current_sgr_attributes["foreground"] = ""

            case parameter if (1 <= parameter <= 9 or
                               22 <= parameter <= 29):
                # font styles
                current_sgr_attributes["style"].add(f"sgr_{parameter}")

            case parameter if 30 <= parameter <= 37:
                # Set foreground color
                current_sgr_attributes["foreground"] = f"sgr_{parameter}"

            case parameter if 40 <= parameter <= 47:
                # Set background color
                current_sgr_attributes["background"] = f"sgr_{parameter}"

            case _:
                raise NotImplementedError("Not supported yet.")

    return current_sgr_attributes


class SequenceParser:

    def __init__(self) -> None:

        self.DEFAULT_SGR_ATTRIBUTES = {"style": set(), "background": "", "foreground": ""}  # to class?
        # refactor -> arg

    def __process_char(
        self,
        char: str,
        mode: str,
        inter_converted: InterConverted,
        current_sgr_attributes: dict,
        current_index: int
    ) -> tuple[InterConverted, int]:
        # https://stackoverflow.com/questions/23058564/checking-a-character-is-fullwidth-or-halfwidth-in-python

        if not inter_converted.validate():
            raise ValueError("inter_converted is invalid.")

        wcharph = WCharPH()

        def is_char_wide(char):
            """Check if the character width is wide."""
            if unicodedata.east_asian_width(char) in ('W', 'F', 'A'):
                return True
            else:
                return False

        def wide_replace_next_char():
            """If the new character is wide, replace the next character."""
            if current_index + 1 > len(inter_converted.text) - 1:
                # index out of range
                inter_converted.text.append(wcharph)
            else:
                if is_char_wide(inter_converted.text[current_index + 1]):
                    # next char is wide
                    inter_converted.text[current_index + 1:current_index + 3] = [wcharph, " "]
                else:
                    inter_converted.text[current_index + 1] = wcharph
        
        is_new_wide = is_char_wide(char)

        match mode:
            case "add":
                if is_new_wide:
                    # new char is wide
                    inter_converted.text.extend([char, wcharph])
                    inter_converted.styles.extend([copy.deepcopy(current_sgr_attributes) for _ in range(2)])
                    # +2 because a placeholder is appended.
                    return inter_converted, current_index + 2
                else:
                    # new char is narrow
                    inter_converted.text.append(char)
                    inter_converted.styles.append(copy.deepcopy(current_sgr_attributes))
                    # +1 because a placeholder is not needed.
                    return inter_converted, current_index + 1

            case "overwrite":
                current_char = inter_converted.text[current_index]

                if is_new_wide:
                    # new char is wide
                    if isinstance(current_char, WCharPH):
                        # current_char is placeholder
                        inter_converted.text[current_index - 1:current_index + 1] = [" ", char]
                        wide_replace_next_char()
                        inter_converted.styles[current_index:current_index + 2] = [copy.deepcopy(current_sgr_attributes) for _ in range(2)]

                    elif is_char_wide(current_char):
                        # current_char is wide
                        inter_converted.text[current_index] = char
                        inter_converted.styles[current_index:current_index + 2] = [copy.deepcopy(current_sgr_attributes) for _ in range(2)]

                    else:
                        # current_char is Narrow
                        inter_converted.text[current_index] = char
                        wide_replace_next_char()
                        inter_converted.styles[current_index:current_index + 2] = [copy.deepcopy(current_sgr_attributes) for _ in range(2)]

                    # +2 because a placeholder is appended.
                    return inter_converted, current_index + 2
                else:
                    # new char is narrow
                    if isinstance(current_char, WCharPH):
                        # current_char is placeholder
                        inter_converted.text[current_index - 1:current_index + 1] = [" ", char]
                        inter_converted.styles[current_index] = copy.deepcopy(current_sgr_attributes)

                    elif is_char_wide(current_char):
                        # current_char is wide
                        inter_converted.text[current_index:current_index + 2] = [char, " "]
                        inter_converted.styles[current_index] = copy.deepcopy(current_sgr_attributes)

                    else:
                        # Narrow
                        inter_converted.text[current_index] = char
                        inter_converted.styles[current_index] = copy.deepcopy(current_sgr_attributes)

                    # +1 because a placeholder is not needed.
                    return inter_converted, current_index + 1
            case _:
                raise ValueError("Incorrect mode argument.")

    def parse_text(
        self,
        sequence: str,
        inter_converted,
        current_sgr_attributes,
        current_index
    ) -> tuple[InterConverted, int]:
        """Parse sequence only containing text."""

        if inter_converted is None:
            inter_converted = InterConverted()

        if current_sgr_attributes is None:
            current_sgr_attributes = copy.copy(self.DEFAULT_SGR_ATTRIBUTES)

        # Fill empty spaces if the cursor is moved.
        # exclude current
        max_index = len(inter_converted.text) - 1
        need = current_index - max_index - 1
        if need > 0:
            inter_converted.text.extend([" "] * need)  # space
            inter_converted.styles.extend([copy.copy(self.DEFAULT_SGR_ATTRIBUTES)] * need)  # default

        # process text
        char_list = list(sequence)
        for char in char_list:

            max_index = len(inter_converted.text) - 1
            if current_index > max_index:
                # add new
                inter_converted, current_index = self.__process_char(char, "add", inter_converted, current_sgr_attributes, current_index)
            else:
                # overwrite
                inter_converted, current_index = self.__process_char(char, "overwrite", inter_converted, current_sgr_attributes, current_index)

        #
        return inter_converted, current_index

    def parse_sgr(
        self,
        sequence: str,
        current_sgr_attributes: dict
    ) -> dict:
        """Parse "Select Graphic Rendition" sequence."""

        if current_sgr_attributes is None:
            current_sgr_attributes = copy.copy(self.DEFAULT_SGR_ATTRIBUTES)

        extracter = ParametersExtractor()
        parameters = extracter.extract_sgr(sequence)

        return sgr_parameters_to_attributes(parameters, current_sgr_attributes)

    def parse_el(
        self,
        sequence: str,
        inter_converted: InterConverted,
        current_index: int
    ) -> InterConverted:
        """Parse "Erase in Line" sequence."""
        # Cursor position does not change.

        if inter_converted is None:
            inter_converted = InterConverted()

        extracter = ParametersExtractor()
        parameter = extracter.extract_el(sequence)

        match parameter:
            case 0:
                # If n is 0, clear from cursor to the end of the line
                # include cursor char
                inter_converted.text = inter_converted.text[0: current_index]
                inter_converted.styles = inter_converted.styles[0: current_index]

            case 1:
                # If n is 1, clear from cursor to beginning of the line.
                # include cursor char
                inter_converted.text[0: current_index + 1] = [" "] * (current_index + 1)  # space
                inter_converted.styles[0: current_index + 1] = [copy.copy(self.DEFAULT_SGR_ATTRIBUTES)] * (current_index + 1)  # default

            case 2:
                # If n is 2, clear entire line.
                inter_converted.clear()

            case _:
                raise RuntimeError()

        return inter_converted

    def parse_ed(
        self,
        sequence: str,
        inter_converted: InterConverted,
        current_index: int,
        parsed_screen: list,
        current_line_index: int
    ) -> tuple[InterConverted, list]:
        """Parse "Erase in Display" sequence."""

        if inter_converted is None:
            inter_converted = InterConverted()

        extracter = ParametersExtractor()
        parameter = extracter.extract_ed(sequence)

        match parameter:
            case 0:
                #  If n is 0 (or missing), clear from cursor to end of screen.
                # Cursor position does not change.
                parsed_screen = parsed_screen[0:current_line_index]

                inter_converted.text = inter_converted.text[0: current_index]
                inter_converted.styles = inter_converted.text[0: current_index]

            case 1:
                # If n is 1, clear from cursor to beginning of the screen.
                # Cursor position does not change.
                parsed_screen[0:current_line_index + 1] = [InterConverted() for _ in range(current_line_index + 1)]  # as newline

                inter_converted.text[0: current_index + 1] = [" "] * (current_index + 1)
                inter_converted.styles[0: current_index + 1] = [copy.copy(self.DEFAULT_SGR_ATTRIBUTES)] * (current_index + 1)

            case 2:
                # If n is 2, clear entire screen (and moves cursor to upper left on DOS ANSI.SYS).
                parsed_screen = []
                inter_converted = InterConverted()

            case 3:
                # If n is 3, clear entire screen and delete all lines saved in the scrollback buffer
                raise NotImplementedError()

            case _:
                raise RuntimeError()

        return inter_converted, parsed_screen

    def parse_cup(
        self,
        sequence: str,
        inter_converted: InterConverted,
        current_index: int,
        parsed_screen: list,
        current_line_index: int
    ) -> dict:
        """Parse "Cursor Position" sequence."""

        extracter = ParametersExtractor()
        parameter = extracter.extract_cup(sequence)

        # Moves the cursor to row n, column m. The values are 1-based.
        next_line_index = parameter[0] - 1
        next_index = parameter[1] - 1

        if inter_converted is not None:
            # append current line to screen
            max_line_index = len(parsed_screen) - 1
            if current_line_index > max_line_index:
                # add new
                parsed_screen.append(copy.deepcopy(inter_converted))
            else:
                # overwrite
                parsed_screen[current_line_index] = copy.deepcopy(inter_converted)

        # Fill empty lines (including current).
        max_line_index = len(parsed_screen) - 1
        need = next_line_index - max_line_index
        if need > 0:
            # Create independent InterConverted
            parsed_screen.extend([InterConverted() for _ in range(need)])

        # move cursor to next_line_index
        inter_converted = parsed_screen[next_line_index]

        current_index = next_index
        current_line_index = next_line_index

        return {
            "inter_converted": inter_converted,
            "current_index": current_index,
            "parsed_screen": parsed_screen,
            "current_line_index": current_line_index
        } 
        
    def parse_newline(
        self,
        sequence: str,
        inter_converted: InterConverted,
        current_index: int,
        parsed_screen: list,
        current_line_index: int
    ) -> dict:
        """Parse "newline("\r\n", "\n", "\r")" sequence."""

        if inter_converted is None:
            inter_converted = InterConverted()

        if sequence not in ("\r\n", "\n", "\r"):
            raise RuntimeError()

        # \r (Carriage Return)
        # moves the cursor to the beginning of the line without advancing to the next line
        if sequence == "\r":
            current_index = 0
            next_line_index = current_line_index
        else:
            next_line_index = current_line_index + 1

        # Fill empty lines (including current).
        max_line_index = len(parsed_screen) - 1
        need = next_line_index - max_line_index
        if need > 0:
            # Create independent InterConverted
            parsed_screen.extend([InterConverted() for _ in range(need)])

        # move cursor to next_line_index
        inter_converted = parsed_screen[next_line_index]

        # Moves the cursor to next row.
        current_line_index = next_line_index

        # "\r\n" as "\r (Carriage Return)" + "\n (Line Feed)"
        # moves the cursor to the beginning and moves the cursor down to the next line
        if sequence == "\r\n":
            current_index = 0

        # \n (Line Feed)
        # moves the cursor down to the next line without returning to the beginning of the line
        # "current_index" does not change

        return {
            "inter_converted": inter_converted,
            "current_index": current_index,
            "parsed_screen": parsed_screen,
            "current_line_index": current_line_index
        }
