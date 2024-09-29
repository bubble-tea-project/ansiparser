"""
ansiparser.structures
~~~~~~~~~~~~~~~~~~~

Data structures used in ansiparser.
"""


class WCharPH:
    """Placeholder for wide characters."""

    def __init__(self) -> None:
        pass


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
