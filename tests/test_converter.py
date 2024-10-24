import pytest
from bs4 import BeautifulSoup
from ansiparser.converter import sgr_attributes_to_css, to_html, to_string
from ansiparser.structures import InterConverted, SgrAttributes, WCharPH


def test_sgr_attributes_to_css():
    # Prepare test SGR attributes
    sgr_attributes = SgrAttributes()
    sgr_attributes.style = {"sgr_1"}
    sgr_attributes.foreground ="sgr_30"
    sgr_attributes.background ="sgr_40"
    
    css_class = sgr_attributes_to_css(sgr_attributes)

    assert css_class == "sgr_1 sgr_30 sgr_40"


def test_to_html_valid():
    # Prepare test InterConverted object
    inter_converted = InterConverted()
    inter_converted.text = ["A", "B"]

    sgr_attributes = SgrAttributes()
    sgr_attributes.style = {"sgr_1", "sgr_2"}
    sgr_attributes.foreground ="sgr_30"
    sgr_attributes.background ="sgr_40"

    sgr_attributes_1 = SgrAttributes()
    sgr_attributes_1.style = {"sgr_1"}
    sgr_attributes_1.foreground ="sgr_30"
    sgr_attributes_1.background ="sgr_40"

    inter_converted.styles = [sgr_attributes,sgr_attributes_1]


    result = to_html(inter_converted)

    assert result.name == "div"
    assert len(result.select("span")) == 2

    assert result.select("span")[0].string == "A"
    assert "sgr_30" in result.select("span")[0]["class"]




def test_to_html_invalid():
    # Prepare an invalid InterConverted object
    inter_converted = InterConverted()
    inter_converted.text = ["A", "B"]

    sgr_attributes = SgrAttributes()
    sgr_attributes.style = {"sgr_1", "sgr_2"}
    sgr_attributes.foreground ="sgr_30"
    sgr_attributes.background ="sgr_40"

   
    inter_converted.styles = [sgr_attributes]

    with pytest.raises(ValueError):
        to_html(inter_converted)


def test_to_string_valid():
    # Prepare test InterConverted object
    inter_converted = InterConverted()
    inter_converted.text = ["A", "B"]
    
    sgr_attributes = SgrAttributes()
    sgr_attributes.style = {"sgr_1", "sgr_2"}
    sgr_attributes.foreground ="sgr_30"
    sgr_attributes.background ="sgr_40"

    inter_converted.styles = [sgr_attributes,sgr_attributes]

    result = to_string(inter_converted)
    assert result == "AB"


def test_to_string_invalid():
    # Prepare an invalid InterConverted object
    inter_converted = InterConverted()
    inter_converted.text = ["A", "B"]

    sgr_attributes = SgrAttributes()
    sgr_attributes.style = {"sgr_1", "sgr_2"}
    sgr_attributes.foreground ="sgr_30"
    sgr_attributes.background ="sgr_40"

    inter_converted.styles = [sgr_attributes]

    with pytest.raises(ValueError):
        to_string(inter_converted)
