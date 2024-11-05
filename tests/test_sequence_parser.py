import copy

import pytest

from ansiparser.sequence_parser import (SequenceParser,
                                        _sgr_parameters_to_attributes)
from ansiparser.structures import InterConverted, SgrAttributes


def test_sgr_parameters_to_attributes_clear():

    sgr_attributes = SgrAttributes()
    sgr_attributes.style = {"bold", "italic"}
    sgr_attributes.foreground = "fg_black"
    sgr_attributes.background = "bg_black"

    parameters = [0]  # Reset or normal
    result = _sgr_parameters_to_attributes(parameters, sgr_attributes)
    assert result.style == set()
    assert result.foreground == ""
    assert result.background == ""


def test_sgr_parameters_to_attributes():

    sgr_attributes = SgrAttributes()

    parameters = [31]  # Set foreground color
    result = _sgr_parameters_to_attributes(parameters, sgr_attributes)
    assert result.foreground == "fg_red"


@pytest.fixture
def sequence_parser():
    return SequenceParser()


@pytest.fixture
def inter_converted():
    return InterConverted()


@pytest.fixture
def sgr_attributes():
    return SgrAttributes()


class TestParseText:

    def test_add(self, sequence_parser, inter_converted, sgr_attributes):

        text = "Hello"
        inter_converted, current_index = sequence_parser.parse_text(text, inter_converted, sgr_attributes, 0)

        assert inter_converted.text == list(text)
        assert len(inter_converted.styles) == len(text)
        assert current_index == len(text)

    def test_overwrite(self, sequence_parser, inter_converted, sgr_attributes):

        inter_converted.text = list("abcde")
        inter_converted.styles = [SgrAttributes() for _ in range(5)]

        text = "XYZ"
        inter_converted, current_index = sequence_parser.parse_text(text, inter_converted, sgr_attributes, 1)

        assert inter_converted.text == list("aXYZe")
        assert current_index == 4  # index at 'e'


def test_parse_sgr(sequence_parser, sgr_attributes):

    sequence = "\x1b[31m"  # Foreground color , red
    result = sequence_parser.parse_sgr(sequence, sgr_attributes)

    assert result.foreground == "fg_red"


class TestParseEl:

    def test_to_end_of_line(self, sequence_parser, inter_converted):

        inter_converted.text = list("Hello World")
        inter_converted.styles = [SgrAttributes() for _ in inter_converted.text]
        current_index = 5
        result = sequence_parser.parse_el("\x1b[0K", inter_converted, current_index)

        assert result.text == list("Hello")

    def test_to_start_of_line(self, sequence_parser, inter_converted):

        inter_converted.text = list("Hello World")
        inter_converted.styles = [SgrAttributes() for _ in inter_converted.text]
        current_index = 5
        result = sequence_parser.parse_el("\x1b[1K", inter_converted, current_index)

        assert result.text == list("      World")

    def test_entire_line(self, sequence_parser, inter_converted):

        inter_converted.text = list("Hello World")
        inter_converted.styles = [SgrAttributes() for _ in inter_converted.text]
        result = sequence_parser.parse_el("\x1b[2K", inter_converted, 5)

        assert result.text == []


class TestParseEd:

    @pytest.fixture
    def parsed_screen(self):

        parsed_screen = []

        inter_converted.text = list("Hello World")
        inter_converted.styles = [SgrAttributes() for _ in inter_converted.text]
        for _ in range(2):
            parsed_screen.append(copy.deepcopy(inter_converted))

        return parsed_screen

    def test_to_end_of_screen(self, sequence_parser, parsed_screen):

        inter_converted = parsed_screen[0]
        current_index = 5
        current_line_index = 0
        inter_converted, parsed_screen = sequence_parser.parse_ed("\x1b[0J", inter_converted, current_index, parsed_screen, current_line_index)

        assert inter_converted.text == list("Hello")
        assert len(parsed_screen) == 1

    def test_to_start_of_screen(self, sequence_parser, parsed_screen):

        inter_converted = parsed_screen[1]
        current_index = 5
        current_line_index = 1
        inter_converted, parsed_screen = sequence_parser.parse_ed("\x1b[1J", inter_converted, current_index, parsed_screen, current_line_index)

        assert inter_converted.text == list("      World")
        assert len(parsed_screen) == 2

    def test_entire_screen(self, sequence_parser, parsed_screen):

        inter_converted = parsed_screen[0]
        current_index = 5
        current_line_index = 0
        inter_converted, parsed_screen = sequence_parser.parse_ed("\x1b[2J", inter_converted, current_index, parsed_screen, current_line_index)

        assert inter_converted.text == []
        assert parsed_screen == []


def test_parse_cup(sequence_parser, inter_converted):

    parsed_screen = [inter_converted]
    result = sequence_parser.parse_cup("\x1b[10;10H", inter_converted, 0, parsed_screen, 0)

    assert result["current_index"] == 9
    assert result["current_line_index"] == 9


def test_parse_newline(sequence_parser, inter_converted):

    parsed_screen = [inter_converted]
    result = sequence_parser.parse_newline("\r\n", inter_converted, 0, parsed_screen, 0)

    assert result["current_index"] == 0
    assert result["current_line_index"] == 1
