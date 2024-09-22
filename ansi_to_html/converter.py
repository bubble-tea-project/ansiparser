from bs4 import BeautifulSoup


class InterConverted:
    """intermediate conversion for ANSI escape."""

    def __init__(self) -> None:

        self.text = []
        self.styles = []

    def clear(self) -> None:

        self.text = []
        self.styles = []


def sgr_parameters_to_attributes(parameters, current_sgr_attributes) -> dict:
    """Convert SGR parameters to attributes."""
    # sgr_attributes = { "style":set() , "background":"" , "foreground":"" }

    for parameter in parameters:

        match parameter:
            case 0:
                # Reset or normal
                current_sgr_attributes["style"].clear()
                current_sgr_attributes["background"] = ""
                current_sgr_attributes["foreground"] = ""

            case parameter if (1 <= parameter <= 9 or
                               22 <= parameter <= 29):
                # font styles
                current_sgr_attributes["style"].add(f"sgr_{parameter}")

            case parameter if 30 <= parameter <= 37:
                # Set foreground color
                current_sgr_attributes["foreground"] = f"sgr_{parameter}"

            case parameter if 40 <= parameter <= 47:
                # Set background color
                current_sgr_attributes["background"] = f"sgr_{parameter}"

            case _:
                raise NotImplementedError("Not supported.")

    return current_sgr_attributes

def sgr_attributes_to_css(sgr_attributes) -> str:
    """Convert SGR attributes to CSS class."""

    font_styles = " ".join(sgr_attributes["style"])
    color_foreground = sgr_attributes["foreground"]
    color_background = sgr_attributes["background"]

    css_class = f"{font_styles} {color_foreground} {color_background}"

    return css_class

def to_html(inter_converted):

    if len(inter_converted.text) != len(inter_converted.styles):
        raise RuntimeError("The text and styles in 'inter_converted' have different lengths.")

    soup = BeautifulSoup("", "html.parser")
    line_div = soup.new_tag("div")

    # If empty (treated as newline).
    if not inter_converted.text:
        return line_div

    line_string = "".join(inter_converted.text) # Note that white space collapses in HTML (if using a formatter).
    last_style = inter_converted.styles[0]

    start_index = 0
    current_index = 0

    for style in inter_converted.styles:

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

def html_lines_to_screen(html_lines):

    soup = BeautifulSoup("", "html.parser")

    screen_div = soup.new_tag("div")
    screen_div["class"] = "screen"

    for line in html_lines:
        line["class"] = "line"
        screen_div.append(line)

    return screen_div
