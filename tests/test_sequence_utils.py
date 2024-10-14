import pytest
from ansiparser.sequence_utils import CSIChecker, ParametersExtractor
from ansiparser import re_pattern


# Sample strings to test against the patterns
sample_string = "Hello World"
sample_ansi_string = "\x1b[1;6H-World!\x1b[1;1HHello"
sample_sgr_string = "\x1b[1;37m推"
sample_erase_display = "\x1B[2J"
sample_erase_line = "\x1B[2K"
sample_cursor_position = "\x1b[24;1H"


class TestCSIChecker:

    @pytest.fixture
    def csi_checker(self):
        return CSIChecker()

    def test_is_csi(self, csi_checker):

        assert csi_checker.is_csi(sample_ansi_string) is True
        assert csi_checker.is_csi(sample_string) is False

    def test_is_sgr_sequence(self, csi_checker):

        assert csi_checker.is_sgr_sequence(sample_sgr_string) is True
        assert csi_checker.is_sgr_sequence(sample_string) is False

    def test_is_ed_sequence(self, csi_checker):

        assert csi_checker.is_ed_sequence(sample_erase_display) is True
        assert csi_checker.is_ed_sequence(sample_erase_line) is False

    def test_is_el_sequence(self, csi_checker):

        assert csi_checker.is_el_sequence(sample_erase_line) is True
        assert csi_checker.is_el_sequence(sample_erase_display) is False

    def test_is_cup_sequence(self, csi_checker):

        assert csi_checker.is_cup_sequence(sample_cursor_position) is True
        assert csi_checker.is_cup_sequence(sample_sgr_string) is False


class TestParametersExtractor:

    @pytest.fixture
    def params_extractor(self):
        return ParametersExtractor()

    def test_extract_sgr(self, params_extractor):

        assert params_extractor.extract_sgr(sample_sgr_string) == [1, 37]

        valid_sgr_reset = "\x1b[m"
        assert params_extractor.extract_sgr(valid_sgr_reset) == [0]

        with pytest.raises(ValueError):
            params_extractor.extract_sgr("Invalid Sequence")

    def test_extract_ed(self, params_extractor):

        assert params_extractor.extract_ed(sample_erase_display) == 2

        valid_ed_no_param = "\x1b[J"
        assert params_extractor.extract_ed(valid_ed_no_param) == 0

        with pytest.raises(ValueError):
            params_extractor.extract_ed("Invalid Sequence")

    def test_extract_el(self, params_extractor):

        assert params_extractor.extract_el(sample_erase_line) == 2

        valid_el_no_param = "\x1b[K"
        assert params_extractor.extract_el(valid_el_no_param) == 0

        with pytest.raises(ValueError):
            params_extractor.extract_el("Invalid Sequence")

    def test_extract_cup(self, params_extractor):

        assert params_extractor.extract_cup(sample_cursor_position) == [24, 1]

        valid_cup_no_param = "\x1b[H"
        assert params_extractor.extract_cup(valid_cup_no_param) == [1, 1]

        with pytest.raises(ValueError):
            params_extractor.extract_cup("Invalid Sequence")
