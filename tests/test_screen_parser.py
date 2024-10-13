import pytest

from ansiparser import screen_parser


def test_apply_backspace():

    assert screen_parser.apply_backspace("hel\x08lo") == "helo"


def test_split_by_ansi():

    assert screen_parser.split_by_ansi("hello\x1B[31mworld\x1B[0m") == ["hello", "\x1B[31m", "world", "\x1B[0m"]
