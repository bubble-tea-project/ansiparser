from . import parser


def from_string(string: str):
    """Initialize parser with a string."""

    return parser.StringParser(string)


def from_screen():
    """Initialize parser with screen mode (terminal)."""

    return parser.ScreenParser()
