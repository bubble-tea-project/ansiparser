from ansiparser.re_pattern import ansi_escape, csi_sequence, sgr_sequence, erase_display_sequence, erase_display_clear_screen, erase_line_sequence, cursor_position_sequence


# Sample strings to test against the patterns
sample_ansi_string = "\x1b[1;6H-World!\x1b[1;1HHello"
sample_sgr_string = "\x1b[1;37m推"
sample_erase_display = "\x1B[2J"
sample_erase_line = "\x1B[2K"
sample_cursor_position = "\x1b[24;1H"


def test_ansi_escape():
    assert ansi_escape.search(sample_ansi_string) is not None
    assert ansi_escape.search("No ANSI escape") is None


def test_csi_sequence():
    assert csi_sequence.search(sample_sgr_string) is not None
    assert csi_sequence.search("Not a CSI sequence") is None


def test_sgr_sequence():
    assert sgr_sequence.search(sample_sgr_string) is not None
    assert sgr_sequence.search("\x1b[1;6H-World") is None


def test_erase_display_sequence():
    assert erase_display_sequence.search(sample_erase_display) is not None
    assert erase_display_sequence.search("\x1B[2K") is None


def test_erase_display_clear_screen():
    assert erase_display_clear_screen.search(sample_erase_display) is not None
    assert erase_display_clear_screen.search("\x1B[1J") is None


def test_erase_line_sequence():
    assert erase_line_sequence.search(sample_erase_line) is not None
    assert erase_line_sequence.search("\x1B[1J") is None


def test_cursor_position_sequence():
    assert cursor_position_sequence.search(sample_cursor_position) is not None
    assert cursor_position_sequence.search("\x1b[34;47m") is None
