import pytest

from ansiparser.converter import sgr_attributes_to_css, to_html, to_string
from ansiparser.structures import InterConverted, SgrAttributes


def test_sgr_attributes_to_css():

    sgr_attributes = SgrAttributes()
    sgr_attributes.style = {'bold'}
    sgr_attributes.foreground = 'fg_blue'
    sgr_attributes.background = 'bg_white'

    assert sgr_attributes_to_css(sgr_attributes) == "bold fg_blue bg_white"


@pytest.fixture()
def valid_inter_converted():

    inter_converted = InterConverted()
    inter_converted.text = ["R", " ", "G"]

    attribute_red = SgrAttributes()
    attribute_red.background = 'fg_red'

    attribute_green = SgrAttributes()
    attribute_green.foreground = 'fg_green'

    inter_converted.styles = [attribute_red, attribute_red, attribute_green]

    return inter_converted


@pytest.fixture()
def invalid_inter_converted():

    inter_converted = InterConverted()
    inter_converted.text = ["R", " ", "G"]

    sgr_attributes = SgrAttributes()

    inter_converted.styles = [sgr_attributes]

    return inter_converted


def test_to_html_valid(valid_inter_converted: InterConverted):

    result = str(to_html(valid_inter_converted))
    answer = '<div class="line"><span class="fg_red">R </span><span class="fg_green">G</span></div>'

    assert result == answer


def test_to_html_invalid(invalid_inter_converted: InterConverted):

    with pytest.raises(ValueError):
        to_html(invalid_inter_converted)


def test_to_string_valid(valid_inter_converted: InterConverted):

    result = to_string(valid_inter_converted)

    assert result == 'R G'


def test_to_string_invalid(invalid_inter_converted: InterConverted):

    with pytest.raises(ValueError):
        to_string(invalid_inter_converted)
