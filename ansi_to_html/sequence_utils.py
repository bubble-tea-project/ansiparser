"""
ansi_to_html.sequence_utils
~~~~~~~~~~~~~~

This module provides functions to check CSI sequences and extract their parameters.
"""

import re
from typing import Pattern

from . import re_pattern


class CSIChecker:

    def __init__(self) -> None:
        pass

    def __is_regex_match(self, regex: str | Pattern, string: str) -> bool:

        match_ = re.search(regex, string)
        if match_ is None:
            return False
        else:
            return True

    def is_csi(self, string: str) -> bool:
        """Return True if the string is "CSI (Control Sequence Introducer)" sequences."""

        return self.__is_regex_match(re_pattern.csi_sequence, string)

    def is_sgr_sequence(self, string: str) -> bool:
        """Return True if the string is "SGR (Select Graphic Rendition)" sequences."""

        return self.__is_regex_match(re_pattern.sgr_sequence, string)

    def is_ed_sequence(self, string: str) -> bool:
        """Return True if the string is "Erase in Display" sequences."""

        return self.__is_regex_match(re_pattern.erase_display_sequence, string)

    def is_el_sequence(self, string: str) -> bool:
        """Return True if the string is "Erase in Line" sequences."""

        return self.__is_regex_match(re_pattern.erase_line_sequence, string)

    def is_cup_sequence(self, string: str) -> bool:
        """Return True if the string is "Cursor Position" sequences."""

        return self.__is_regex_match(re_pattern.cursor_position_sequence, string)


class ParametersExtractor:

    def __init__(self) -> None:
        pass

    def extract_sgr(self, sequence: str) -> list:
        """Extract parameters for "SGR (Select Graphic Rendition)" sequences."""

        match_ = re.search(re_pattern.sgr_sequence, sequence)
        if match_ is None:
            raise ValueError('Not "SGR (Select Graphic Rendition)" sequences.')

        parameters_str = match_.group(1)
        if parameters_str == "":
            # CSI m is treated as CSI 0 m (reset / normal).
            return [0]
        else:
            # All common sequences just use the parameters as a series of semicolon-separated numbers such as 1;2;3
            return list(map(int, parameters_str.split(';')))

    def extract_ed(self, sequence: str) -> int:
        """Extract parameters for "Erase in Display" sequences."""

        match_ = re.search(re_pattern.erase_display_sequence, sequence)
        if match_ is None:
            raise ValueError('Not "Erase in Display" sequences.')

        parameters_str = match_.group(1)
        if parameters_str == "":
            # [J as [0J
            return 0
        else:
            return int(parameters_str)

    def extract_el(self, sequence: str) -> int:
        """Extract parameters for "Erase in Line" sequences."""

        match_ = re.search(re_pattern.erase_line_sequence, sequence)
        if match_ is None:
            raise ValueError('Not "Erase in Line" sequences.')

        parameters_str = match_.group(1)
        if parameters_str == "":
            # [K as [0K
            return 0
        else:
            return int(parameters_str)

    def extract_cup(self, sequence: str) -> list:
        """Extract parameters for "Cursor Position" sequences."""

        match_ = re.search(re_pattern.cursor_position_sequence, sequence)
        if match_ is None:
            raise ValueError('Not "Cursor Position" sequences.')

        parameters_str = match_.group(1)
        if parameters_str == "":
            # [H as [1;1H
            return [1, 1]
        else:
            # All common sequences just use the parameters as a series of semicolon-separated numbers such as 1;2;3
            results = parameters_str.split(';')
            if len(results) != 2:
                raise RuntimeError("Position parameters error.")

            # The values are 1-based, and default to 1 (top left corner) if omitted.
            if results[0] == "":
                results[0] = "1"
            if results[1] == "":
                results[1] = "1"

            return list(map(int, results))
