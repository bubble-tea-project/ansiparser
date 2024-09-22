"""
ansi_to_html.api
~~~~~~~~~~~~~~

This module implements the ansi_to_html API.
"""

from . import screen_parser


def new_screen() -> screen_parser.ScreenParser:
    """Initialize new  parser for screen """

    return screen_parser.ScreenParser()


def from_inter_converted(parsed_screen: list) -> screen_parser.ScreenParser:
    """Initialize from old inter_converted."""

    screen_parser_class = screen_parser.ScreenParser()
    screen_parser_class.from_parsed_screen(parsed_screen)

    return screen_parser_class
