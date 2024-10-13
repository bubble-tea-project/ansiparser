from ansiparser.structures import InterConverted, SgrAttributes, WCharPH


def test_wcharph_init():

    wcharph = WCharPH()

    assert isinstance(wcharph, WCharPH)


class TestSgrAttributes:

    def test_init(self):

        sgr_attr = SgrAttributes()

        assert sgr_attr.style == set()
        assert sgr_attr.background == ""
        assert sgr_attr.foreground == ""

    def test_equality(self):

        sgr1 = SgrAttributes()
        sgr2 = SgrAttributes()
        assert sgr1 == sgr2

        sgr1.style.add("sgr_1")
        assert sgr1 != sgr2

    def test_clear(self):

        sgr = SgrAttributes()
        sgr.style.add("sgr_1")
        sgr.background = "sgr_40"
        sgr.foreground = "sgr_30"
        sgr.clear()

        assert sgr.style == set()
        assert sgr.background == ""
        assert sgr.foreground == ""

    def test_empty(self):

        sgr = SgrAttributes()
        assert sgr.empty()

        sgr.style.add("sgr_1")
        assert not sgr.empty()


class TestInterConverted:

    def test_init(self):

        inter_converted = InterConverted()
        assert inter_converted.text == []
        assert inter_converted.styles == []

    def test_interconverted_clear(self):

        inter_converted = InterConverted()
        inter_converted.text.append("t")
        inter_converted.styles.append(SgrAttributes())
        inter_converted.clear()

        assert inter_converted.text == []
        assert inter_converted.styles == []

    def test_empty(self):

        inter_converted = InterConverted()
        assert inter_converted.empty()

        inter_converted.text.append("sample")
        assert not inter_converted.empty()

    def test_interconverted_validate(self):

        inter_converted = InterConverted()
        inter_converted.text = ["t", "e", "s", "t"]
        inter_converted.styles = [SgrAttributes() for _ in range(4)]
        assert inter_converted.validate()

        inter_converted.text.append("n")
        assert not inter_converted.validate()
