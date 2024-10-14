import pytest
from ansiparser.api import new_screen, from_screen
from ansiparser.screen_parser import ScreenParser

from ansiparser.structures import InterConverted, SgrAttributes


class TestAPI:

    def test_new_screen_default(self):
        
        ansip_screen = new_screen()
        assert isinstance(ansip_screen, ScreenParser)
        assert ansip_screen.screen_height == 24
        assert ansip_screen.screen_width == 80

    def test_new_screen_custom(self):
        
        ansip_screen = new_screen(height=30, width=100)

        assert isinstance(ansip_screen, ScreenParser)
        assert ansip_screen.screen_height == 30
        assert ansip_screen.screen_width == 100

    def test_from_screen(self):

        inter_converted = InterConverted()
        inter_converted.text = ["t", "e", "s", "t"]
        inter_converted.styles = [SgrAttributes() for _ in range(4)]

        parsed_screen = [inter_converted , inter_converted]
        
  
        ansip_screen = from_screen(parsed_screen)
        assert isinstance(ansip_screen, ScreenParser)
        # assert ansip_screen.get_parsed_screen() == parsed_screen

    def test_from_screen_invalid(self):
        
        invalid_parsed_screen = None
        
        with pytest.raises(TypeError):
            from_screen(invalid_parsed_screen)

