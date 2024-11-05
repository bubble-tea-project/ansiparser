import pytest

from ansiparser.sequence_utils import CSIChecker, ParametersExtractor


class TestCSIChecker:

    @pytest.fixture
    def csi_checker(self):
        return CSIChecker()

    def test_is_csi(self, csi_checker: CSIChecker):

        assert csi_checker.is_csi("\x1b[1;6H-World!\x1b[1;1HHello") is True
        assert csi_checker.is_csi("Not a CSI sequence") is False

    def test_is_sgr_sequence(self, csi_checker: CSIChecker):

        assert csi_checker.is_sgr_sequence("\x1b[1;37m推") is True
        assert csi_checker.is_sgr_sequence("\x1b[1;6H-World") is False

    def test_is_ed_sequence(self, csi_checker: CSIChecker):

        assert csi_checker.is_ed_sequence("\x1B[1J") is True
        assert csi_checker.is_ed_sequence("\x1B[2K") is False

    def test_is_el_sequence(self, csi_checker: CSIChecker):

        assert csi_checker.is_el_sequence("\x1B[2K") is True
        assert csi_checker.is_el_sequence("\x1B[1J") is False

    def test_is_cup_sequence(self, csi_checker: CSIChecker):

        assert csi_checker.is_cup_sequence("\x1b[24;1H") is True
        assert csi_checker.is_cup_sequence("\x1b[34;47m") is False


class TestParametersExtractor:

    @pytest.fixture
    def params_extractor(self):
        return ParametersExtractor()

    def test_extract_sgr(self, params_extractor: ParametersExtractor):

        assert params_extractor.extract_sgr("\x1b[1;37m推") == [1, 37]

        # default parameters
        assert params_extractor.extract_sgr("\x1b[m") == [0]

        with pytest.raises(ValueError):
            params_extractor.extract_sgr("Invalid Sequence")

    def test_extract_ed(self, params_extractor: ParametersExtractor):

        assert params_extractor.extract_ed("\x1B[2J") == 2

        # default parameters
        assert params_extractor.extract_ed("\x1b[J") == 0

        with pytest.raises(ValueError):
            params_extractor.extract_ed("Invalid Sequence")

    def test_extract_el(self, params_extractor: ParametersExtractor):

        assert params_extractor.extract_el("\x1B[2K") == 2

        # default parameters
        assert params_extractor.extract_el("\x1b[K") == 0

        with pytest.raises(ValueError):
            params_extractor.extract_el("Invalid Sequence")

    def test_extract_cup(self, params_extractor: ParametersExtractor):

        assert params_extractor.extract_cup("\x1b[24;1H") == [24, 1]

        # default parameters
        assert params_extractor.extract_cup("\x1b[H") == [1, 1]

        with pytest.raises(ValueError):
            params_extractor.extract_cup("Invalid Sequence")
