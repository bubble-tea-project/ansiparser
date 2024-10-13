"""
ansiparser.re_pattern
~~~~~~~~~~~~

This module implements commonly used regular expression patterns for ansiparser.
"""

import re


# ANSI escape sequences
# https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
# r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
ansi_escape = re.compile(R'''
(   # capturing group for re.split
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
)
''', re.VERBOSE)

# CSI (Control Sequence Introducer) sequences
# r'\x1B(?:\[[0-?]*[ -/]*[@-~])'
csi_sequence = re.compile(R'''
    \x1B  # ESC
    (?:   # [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)

# SGR (Select Graphic Rendition)
# r'\x1B(?:\[([\d;]*)m)'
sgr_sequence = re.compile(R'''
    \x1B  # ESC
    (?:   # [ for CSI, followed by a control sequence
        \[
        (  # Group for parameters
            [\d;]*  # Parameter bytes
        )
        m   # Final byte                              
    )
''', re.VERBOSE)

# Erase in Display
# r'\x1B(?:\[([\d;]*)J)'
erase_display_sequence = re.compile(R'''
    \x1B  # ESC
    (?:   # [ for CSI, followed by a control sequence
        \[
        (  # Group for parameters
            [\d;]*  # Parameter bytes
        )
        J   # Final byte                              
    )
''', re.VERBOSE)

# Erase in Display - clear entire screen
# r'\x1B(?:\[2J)'
erase_display_clear_screen = re.compile(R'''
    (
        \x1B  # ESC
        (?:   # [ for CSI, followed by a control sequence
            \[
            2  # Parameter bytes
            J  # Final byte 
        )
    )
''', re.VERBOSE)

# Erase in Line
# r'\x1B(?:\[([\d;]*)K)'
erase_line_sequence = re.compile(R'''
    \x1B  # ESC
    (?:   # [ for CSI, followed by a control sequence
        \[
        (  # Group for parameters
            [\d;]*  # Parameter bytes
        )
        K   # Final byte                              
    )
''', re.VERBOSE)

# Cursor Position
# r'\x1B(?:\[([\d;]*)H)'
cursor_position_sequence = re.compile(R'''
    \x1B  # ESC
    (?:   # [ for CSI, followed by a control sequence
        \[
        (  # Group for parameters
            [\d;]*  # Parameter bytes
        )
        H   # Final byte                              
    )
''', re.VERBOSE)
