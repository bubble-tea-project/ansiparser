"""
ansiparser.structures
~~~~~~~~~~~~~~~~~~~

Data structures used in ansiparser.
"""


class WCharPH:
    """Placeholder for wide characters."""

    def __init__(self) -> None:
        pass


class SgrAttributes:
    """
    A class to represent the SGR (Select Graphic Rendition) attributes for text formatting.

    Attributes:
        style (set): A set of styles applied to the text, such as bold, italic, underline, etc.
        background (str): The background color of the text.
        foreground (str): The foreground (text) color.
    """

    def __init__(self) -> None:

        self.style = set()
        self.background = ""
        self.foreground = ""

    def __eq__(self, other) -> bool:
        """
        Compare this SgrAttributes instance with another for equality.

        Returns:
            bool: True if the all attributes are equal, False otherwise.
        """
        if isinstance(other, SgrAttributes):

            return (self.style == other.style and
                    self.background == other.background and
                    self.foreground == other.foreground)
        else:
            return False

    def clear(self) -> None:
        """Remove all elements from the SgrAttributes."""
        self.style.clear()
        self.background = ""
        self.foreground = ""


class InterConverted:
    """Single-line intermediate conversion of ANSI escape codes."""

    def __init__(self) -> None:

        self.text = []
        self.styles = []

    def clear(self) -> None:
        """Remove all elements from the InterConverted."""
        self.text = []
        self.styles = []

    def empty(self) -> bool:
        """Return True if the InterConverted is empty, False otherwise."""
        if (not self.text and
                not self.styles):
            return True
        else:
            return False

    def validate(self) -> bool:
        """Return True if the text and styles in InterConverted have the same length; 
        otherwise, return False."""
        if len(self.text) == len(self.styles):
            return True
        else:
            return False
