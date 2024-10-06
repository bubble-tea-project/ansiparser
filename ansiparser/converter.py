"""
ansiparser.converter
~~~~~~~~~~~~~~

This module provides a converter to convert InterConverted to HTML or string.
"""

import bs4
from bs4 import BeautifulSoup

from .structures import InterConverted, SgrAttributes, WCharPH


def html_lines_to_screen(html_lines: list) -> bs4.element.Tag:
    """Merge multiple line <div> elements into a single screen <div>."""
    soup = BeautifulSoup("", "html.parser")

    screen_div = soup.new_tag("div")
    screen_div["class"] = "screen"

    for line in html_lines:
        line["class"] = "line"
        screen_div.append(line)

    return screen_div


def sgr_attributes_to_css(sgr_attributes: SgrAttributes) -> str:
    """Convert SGR attributes to CSS class."""

    font_styles = " ".join(sgr_attributes.style)
    color_foreground = sgr_attributes.foreground
    color_background = sgr_attributes.background

    css_class = [font_styles, color_foreground, color_background]

    # Removes redundant spaces.
    return " ".join(filter(None, css_class))


def to_html(inter_converted: InterConverted, placeholder=False) -> bs4.element.Tag:
    """convert InterConverted to HTML"""

    if not inter_converted.validate():
        raise ValueError("inter_converted is invalid.")

    soup = BeautifulSoup("", "html.parser")
    line_div = soup.new_tag("div")

    # If empty, treat as a newline.
    if inter_converted.empty():
        return soup.new_tag("br")

    # Process placeholders for wide characters.
    filtered_char = []
    filtered_style = []
    for index, item in enumerate(inter_converted.text):

        # if ignore placeholder
        if (isinstance(item, WCharPH) and
            placeholder is True):
            # replace placeholders with spaces
            filtered_char.append(" ")
            filtered_style.append(inter_converted.styles[index])

        if not isinstance(item, WCharPH):
            filtered_char.append(item)
            filtered_style.append(inter_converted.styles[index])

    # convert
    line_string = "".join(filtered_char)
    last_style = filtered_style[0]

    start_index = 0
    current_index = 0

    for style in filtered_style:
        # Until a different style is encountered.
        if last_style != style:
            tmp_span = soup.new_tag("span")
            tmp_span["class"] = sgr_attributes_to_css(last_style)
            tmp_span.string = line_string[start_index:current_index]

            line_div.append(tmp_span)

            start_index += len(line_string[start_index:current_index])

        last_style = style
        current_index += 1

    # last element
    tmp_span = soup.new_tag("span")
    tmp_span["class"] = sgr_attributes_to_css(last_style)
    tmp_span.string = line_string[start_index:current_index]

    line_div.append(tmp_span)

    return line_div


def to_string(inter_converted: InterConverted, placeholder=False) -> str:
    """convert InterConverted to string"""

    if not inter_converted.validate():
        raise ValueError("inter_converted is invalid.")

    # If empty, treat as a newline.
    if inter_converted.empty():
        return ""

    # Process placeholders for wide characters.
    filtered_char = []
    for item in inter_converted.text:

        # if ignore placeholder
        if (isinstance(item, WCharPH) and
                placeholder is True):
            # replace placeholders with spaces
            filtered_char.append(" ")

        if not isinstance(item, WCharPH):
            filtered_char.append(item)

    return "".join(filtered_char)
