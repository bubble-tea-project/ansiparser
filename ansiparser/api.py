"""
ansiparser.api
~~~~~~~~~~~~~~

This module implements the ansiparser API.
"""

from __future__ import annotations

import typing

from . import screen_parser

if typing.TYPE_CHECKING:
    from collections import deque


def new_screen(height=24,width=80) -> screen_parser.ScreenParser:
    """Initialize the ScreenParser for a new screen."""
    
    return screen_parser.ScreenParser(screen_height=height,screen_width=width)


def from_screen(parsed_screen: list) -> screen_parser.ScreenParser:
    """Initialize the ScreenParser from an existing parsed screen."""

    screen_parser_class = screen_parser.ScreenParser()
    screen_parser_class._from_parsed_screen(parsed_screen)

    return screen_parser_class
