"""
ansiparser Library
~~~~~~~~~~~~~~

AnsiParser is a convenient library for converting ANSI escape sequences into text or HTML.

Basic usage:
    import ansiparser

    ansip_screen = ansiparser.new_screen()
    ansip_screen.put("\x1b[1;6H-World!\x1b[1;1HHello")

    ansip_screen.parse()
    converted = ansip_screen.to_formatted_string()

    print(converted) # ['Hello-World!']

"""

from .api import new_screen, from_screen

