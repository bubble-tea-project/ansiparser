import pytest
from ansiparser.sequence_parser import SequenceParser, _sgr_parameters_to_attributes
from ansiparser.structures import InterConverted, SgrAttributes, WCharPH


# Test _sgr_parameters_to_attributes
def test_sgr_parameters_to_attributes_clear():

    sgr_attributes = SgrAttributes()
    sgr_attributes.style = {"sgr_1", "sgr_2"}
    sgr_attributes.foreground = "sgr_30"
    sgr_attributes.background = "sgr_40"

    parameters = [0]  # Reset or normal
    result = _sgr_parameters_to_attributes(parameters, sgr_attributes)
    assert result.style == set()
    assert result.foreground == ""
    assert result.background == ""


def test_sgr_parameters_to_attributes(sgr_attributes):

    sgr_attributes = SgrAttributes()

    parameters = [31]  # Set foreground color to sgr_31
    result = _sgr_parameters_to_attributes(parameters, sgr_attributes)
    assert result.foreground == "sgr_31"


@pytest.fixture
def sequence_parser():
    return SequenceParser()


@pytest.fixture
def inter_converted():
    return InterConverted()


@pytest.fixture
def sgr_attributes():
    return SgrAttributes()


# Test parse_text
def test_parse_text_add(sequence_parser, inter_converted, sgr_attributes):
    text = "Hello"
    inter_converted, current_index = sequence_parser.parse_text(text, inter_converted, sgr_attributes, 0)

    assert inter_converted.text == list(text)
    assert len(inter_converted.styles) == len(text)
    assert current_index == len(text)


def test_parse_text_overwrite(sequence_parser, inter_converted, sgr_attributes):
    inter_converted.text = list("abcde")
    inter_converted.styles = [SgrAttributes() for _ in range(5)]

    text = "XYZ"
    inter_converted, current_index = sequence_parser.parse_text(text, inter_converted, sgr_attributes, 1)
    assert inter_converted.text == list("aXYZe")
    assert current_index == 4  # should end after "Z"


# Test parse_sgr
def test_parse_sgr(sequence_parser, sgr_attributes):
    sequence = "\x1b[31m"  # Foreground color to sgr_31
    result = sequence_parser.parse_sgr(sequence, sgr_attributes)
    assert result.foreground == "sgr_31"


# Test parse_el
def test_parse_el_clear_to_end_of_line(sequence_parser, inter_converted):
    inter_converted.text = list("Hello World")
    inter_converted.styles = [SgrAttributes() for _ in inter_converted.text]
    current_index = 5
    result = sequence_parser.parse_el("\x1b[0K", inter_converted, current_index)
    assert result.text == list("Hello")


def test_parse_el_clear_to_start_of_line(sequence_parser, inter_converted):
    inter_converted.text = list("Hello World")
    inter_converted.styles = [SgrAttributes() for _ in inter_converted.text]
    current_index = 5
    result = sequence_parser.parse_el("\x1b[1K", inter_converted, current_index)
    assert result.text == list("      World")


def test_parse_el_clear_entire_line(sequence_parser, inter_converted):
    inter_converted.text = list("Hello World")
    inter_converted.styles = [SgrAttributes() for _ in inter_converted.text]
    result = sequence_parser.parse_el("\x1b[2K", inter_converted, 5)
    assert result.text == []


# Test parse_ed
def test_parse_ed_clear_to_end_of_screen(sequence_parser, inter_converted):
    inter_converted.text = list("Hello World")
    parsed_screen = [inter_converted]

    current_index = 5
    current_line_index = 0
    inter_converted, parsed_screen = sequence_parser.parse_ed("\x1b[0J", inter_converted, current_index, parsed_screen, current_line_index)
    assert inter_converted.text == list("Hello")
    assert len(parsed_screen) == 0


def test_parse_ed_clear_entire_screen(sequence_parser, inter_converted):
    inter_converted.text = list("Hello World")
    parsed_screen = [inter_converted]

    current_index = 5
    current_line_index = 0
    inter_converted, parsed_screen = sequence_parser.parse_ed("\x1b[2J", inter_converted, current_index, parsed_screen, current_line_index)
    assert inter_converted.text == []
    assert parsed_screen == []


# Test parse_cup
def test_parse_cup(sequence_parser, inter_converted):
    parsed_screen = [inter_converted]
    result = sequence_parser.parse_cup("\x1b[10;10H", inter_converted, 0, parsed_screen, 0)
    assert result["current_index"] == 9
    assert result["current_line_index"] == 9


# Test parse_newline
def test_parse_newline(sequence_parser, inter_converted):
    parsed_screen = [inter_converted]
    result = sequence_parser.parse_newline("\r\n", inter_converted, 0, parsed_screen, 0)
    assert result["current_index"] == 0
    assert result["current_line_index"] == 1
