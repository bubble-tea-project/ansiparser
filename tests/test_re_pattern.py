from ansiparser.re_pattern import *


def test_ansi_escape():

    assert ansi_escape.search("\x1b[1;6H-World!\x1b[1;1HHello") is not None
    assert ansi_escape.search("No ANSI escape") is None


def test_csi_sequence():

    assert csi_sequence.search("\x1b[1;6H-World!\x1b[1;1HHello") is not None
    assert csi_sequence.search("Not a CSI sequence") is None


def test_sgr_sequence():

    assert sgr_sequence.search("\x1b[1;37m推") is not None
    assert sgr_sequence.search("\x1b[1;6H-World") is None


def test_erase_display_sequence():

    assert erase_display_sequence.search("\x1B[1J") is not None
    assert erase_display_sequence.search("\x1B[2K") is None


def test_erase_display_clear_screen():

    assert erase_display_clear_screen.search("\x1B[2J") is not None
    assert erase_display_clear_screen.search("\x1B[1J") is None


def test_erase_line_sequence():

    assert erase_line_sequence.search("\x1B[2K") is not None
    assert erase_line_sequence.search("\x1B[1J") is None


def test_cursor_position_sequence():

    assert cursor_position_sequence.search("\x1b[24;1H") is not None
    assert cursor_position_sequence.search("\x1b[34;47m") is None
