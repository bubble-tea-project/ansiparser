"""
ansiparser.utils
~~~~~~~~~~~~~~

This module provides utilities used within `ansiparser`.
"""


SGR_MAP = {
    1: "bold",
    2: "dim",
    3: "italic",
    4: "underline",
    5: "slow_blink",
    6: "rapid_blink",
    7: "swap",
    8: "hide",
    9: "strikethrough",

    22: "normal",
    23: "no_italic",
    24: "no_underlined",
    25: "no_blinking",
    27: "no_swap",
    28: "show",
    29: "no_strikethrough",

    30: "fg_black",
    31: "fg_red",
    32: "fg_green",
    33: "fg_yellow",
    34: "fg_blue",
    35: "fg_magenta",
    36: "fg_cyan",
    37: "fg_white",

    40: "bg_black",
    41: "bg_red",
    42: "bg_green",
    43: "bg_yellow",
    44: "bg_blue",
    45: "bg_magenta",
    46: "bg_cyan",
    47: "bg_white",

    90: "fg_brigh_black",
    91: "fg_brigh_red",
    92: "fg_brigh_green",
    93: "fg_brigh_yellow",
    94: "fg_brigh_blue",
    95: "fg_brigh_magenta",
    96: "fg_brigh_cyan",
    97: "fg_brigh_white",

    100: "bg_brigh_black",
    101: "bg_brigh_red",
    102: "bg_brigh_green",
    103: "bg_brigh_yellow",
    104: "bg_brigh_blue",
    105: "bg_brigh_magenta",
    106: "bg_brigh_cyan",
    107: "bg_brigh_white"
}
