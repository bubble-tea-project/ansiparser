import pytest

from ansiparser.api import from_screen, new_screen
from ansiparser.screen_parser import ScreenParser
from ansiparser.structures import InterConverted, SgrAttributes


class TestNewScreen:

    def test_default(self):

        ansip_screen = new_screen()

        assert isinstance(ansip_screen, ScreenParser)
        assert ansip_screen.screen_height == 24
        assert ansip_screen.screen_width == 80

    def test_custom(self):

        ansip_screen = new_screen(height=30, width=100)

        assert isinstance(ansip_screen, ScreenParser)
        assert ansip_screen.screen_height == 30
        assert ansip_screen.screen_width == 100


class TestfromScreen:

    def test_normal(self):

        normal_parsed_screen = []

        for line in range(2):
            inter_converted = InterConverted()
            inter_converted.text = ["t", "e", "s", "t"]
            inter_converted.styles = [SgrAttributes() for char in range(4)]

            normal_parsed_screen.append(inter_converted)

        ansip_screen = from_screen(normal_parsed_screen)
        assert isinstance(ansip_screen, ScreenParser)

    def test_invalid(self):

        invalid_parsed_screen = None

        with pytest.raises(TypeError):
            from_screen(invalid_parsed_screen)
