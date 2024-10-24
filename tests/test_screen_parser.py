import pytest
from ansiparser.screen_parser import ScreenParser, apply_backspace, split_by_ansi
from ansiparser.structures import InterConverted


def test_apply_backspace():

    assert apply_backspace("hel\x08lo") == "helo"


def test_split_by_ansi():

    assert split_by_ansi("hello\x1B[31mworld\x1B[0m") == ["hello", "\x1B[31m", "world", "\x1B[0m"]



@pytest.fixture
def screen_parser():
    """Fixture to provide a fresh ScreenParser instance."""
    return ScreenParser()


def test_put(screen_parser):
    """Test putting strings into screen_buffer."""
    screen_parser.put("Hello")
    assert len(screen_parser._buffer()) == 1
    assert screen_parser._buffer()[0] == ["Hello"]

    
    # Add a screen clear sequence and check the buffer
    screen_parser.put("\x1B[2J")
    assert len(screen_parser._buffer()) == 2
    assert screen_parser._buffer()[-1] == ["\x1B[2J"]
    assert screen_parser.last_screen_finish is True


def test_parse(screen_parser):
    """Test parsing a string and converting it into parsed_screen."""
    screen_parser.put("Hello\nWorld")
    screen_parser.parse()
    parsed_screen = screen_parser.get_parsed_screen()

    assert len(parsed_screen) == 2
    assert isinstance(parsed_screen[0], InterConverted)
    assert isinstance(parsed_screen[1], InterConverted)


def test_clear(screen_parser):
    """Test clearing the current parsed_screen."""
    screen_parser.put("Hello\nWorld")
    screen_parser.parse()
    screen_parser.clear()

    assert screen_parser.get_parsed_screen() == []
    assert screen_parser.current_line_index == 0
    assert screen_parser.current_index == 0



def test_to_formatted_string(screen_parser):
    """Test converting the parsed_screen to a formatted string."""
    screen_parser.put("Hello\nWorld")
    screen_parser.parse()

    formatted_string = screen_parser.to_formatted_string()
    assert formatted_string == ["Hello", "     World"]


def test_to_html(screen_parser):
    """Test converting the parsed_screen to HTML."""
    screen_parser.put("Hello\nWorld")
    screen_parser.parse()

    html_output = screen_parser.to_html()
    assert html_output == ['<div class="line"><span class="">Hello</span></div>','<div class="line"><span class="">     World</span></div>']




