import re
from collections import deque

from . import converter, re_pattern


def split_by_ansi( string ) -> list:
    """Split the string by ANSI escape sequences."""

    results = re.split( re_pattern.ansi_escape , string )

    # Remove empty strings from the results of re.split
    results = list(filter(None, results))

    # If there is only a string, return [string]
    return results


    # # Only has string, no ansi escape
    # if re.search(re_pattern.ansi_escape, raw_string) is None:
    #     return []

    # split_positions = []
    # previous_end = 0
    # for match_ in re.finditer(R"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", raw_string):
                
    #     # Check if there is text between the escape characters
    #     if match_.start() != previous_end:
    #         split_positions.append( (previous_end, match_.start()) )

    #     # add escape position
    #     split_positions.append( match_.span() )

    #     previous_end = match_.end()

    # # Check if there is text at the end.
    # if split_positions[-1][1] != len(raw_string):
    #     split_positions.append( (split_positions[-1][1],len(raw_string)) )


    # return split_positions


class CSIChecker:

    def __init__(self) -> None:
        pass

    def __is_regex_match(self , regex , string) -> bool:
        
        match_ = re.search(regex, string)
        if match_ is None:
            return False
        else:
            return True


    def is_csi(self , string) -> bool:
        """Return True if the string is "CSI (Control Sequence Introducer)" sequences."""
        
        return self.__is_regex_match(re_pattern.csi_sequence,string)
    
    def is_sgr_sequence(self , string) -> bool:
        """Return True if the string is "SGR (Select Graphic Rendition)" sequences."""
        
        return self.__is_regex_match(re_pattern.sgr_sequence,string)

    def is_ed_sequence(self , string) -> bool:
        """Return True if the string is "Erase in Display" sequences."""

        return self.__is_regex_match(re_pattern.erase_display_sequence,string)

    def is_el_sequence(self , string) -> bool:
        """Return True if the string is "Erase in Line" sequences."""

        return self.__is_regex_match(re_pattern.erase_line_sequence,string)

    def is_cup_sequence(self , string) -> bool:
        """Return True if the string is "Cursor Position" sequences."""
    
        return self.__is_regex_match(re_pattern.cursor_position_sequence,string)


class ParametersExtractor:

    def __init__(self) -> None:
        pass

    def extract_sgr(self , sequence) -> list:
        """Extract parameters for "SGR (Select Graphic Rendition)" sequences."""
  
        
        match_ = re.search( re_pattern.sgr_sequence , sequence )
        if match_ is None:
            raise RuntimeError('Not "SGR (Select Graphic Rendition)" sequences.')

        
        parameters_str = match_.group(1)
        if parameters_str == "":
            # CSI m is treated as CSI 0 m (reset / normal).
            return [0]
        else:
            # All common sequences just use the parameters as a series of semicolon-separated numbers such as 1;2;3
            return list(map(int, parameters_str.split(';')))

    def extract_ed(self, sequence ) -> int:
        """Extract parameters for "Erase in Display" sequences."""
        
    
        match_ = re.search( re_pattern.erase_display_sequence , sequence )
        if match_ is None:
            raise RuntimeError('Not "Erase in Display" sequences.')


        parameters_str = match_.group(1)
        if parameters_str == "":
            # [J as [0J
            return 0
        else:
            return int( parameters_str )

    def extract_el(self, sequence ) -> int:
        """Extract parameters for "Erase in Line" sequences."""
        

        match_ = re.search( re_pattern.erase_line_sequence , sequence )
        if match_ is None:
            raise RuntimeError('Not "Erase in Line" sequences.')


        parameters_str = match_.group(1)
        if parameters_str == "":
            # [K as [0K
            return 0
        else:
            return int( parameters_str )

    def extract_cup(self , sequence) -> list:
        """Extract parameters for "Cursor Position" sequences."""


        match_ = re.search( re_pattern.cursor_position_sequence , sequence )
        if match_ is None:
            raise RuntimeError('Not "Cursor Position" sequences.')


        parameters_str = match_.group(1)
        if parameters_str == "":
            # [H as [1;1H
            return [1,1]
        else:
            # All common sequences just use the parameters as a series of semicolon-separated numbers such as 1;2;3
            results = parameters_str.split(';')
            if len(results) != 2 :
                raise RuntimeError("Position parameters error.")

            # The values are 1-based, and default to 1 (top left corner) if omitted. 
            if results[0] == "":
                results[0] = "1"
            if results[1] == "":
                results[1] = "1"

            return list( map(int, results) )


class SequenceParser:

    def __init__(self) -> None:
        # refactor ,to class  : sgr_attributes , max_index , copy?
        self.default_sgr_attributes = { "style":set() , "background":"" , "foreground":"" }
        
    def parse_text(self, text: str, inter_converted , current_sgr_attributes , current_index) -> tuple[converter.InterConverted , int]:
        """Parse sequence only containing text."""
        
        # Fill empty spaces if the cursor is moved.
        # exclude current
        max_index = len(inter_converted.text) - 1
        need = current_index - max_index - 1
        if need > 0:
            inter_converted.text.extend( [" "] * need ) # space
            inter_converted.styles.extend( [self.default_sgr_attributes] * need ) # default


        char_list = list(text)
        for char in char_list: 
            
            max_index = len(inter_converted.text) - 1

            if current_index > max_index:
                # add new
                inter_converted.text.append( char )
                inter_converted.styles.append( current_sgr_attributes.copy() )
            else:
                # overwrite 
                inter_converted.text[current_index] = char
                inter_converted.styles[current_index] = current_sgr_attributes.copy()

            current_index += 1


        return inter_converted , current_index 
    
    def parse_sgr(self , sequence: str , current_sgr_attributes) -> dict:
        """Parse "Select Graphic Rendition" sequence."""

        extracter = ParametersExtractor()
        parameters = extracter.extract_sgr(sequence)
        
        return converter.sgr_parameters_to_attributes(parameters,current_sgr_attributes)
    
    def parse_el(self, sequence, inter_converted, current_index):
        """Parse "Erase in Line" sequence."""
        # Cursor position does not change.
        
        extracter = ParametersExtractor()
        parameter = extracter.extract_el(sequence)

        match parameter:
            case 0:
                # If n is 0, clear from cursor to the end of the line
                # include cursor char
                inter_converted.text = inter_converted.text[ 0 : current_index ]
                inter_converted.styles = inter_converted.text[ 0 : current_index ]

            case 1:
                # If n is 1, clear from cursor to beginning of the line.
                # include cursor char
                inter_converted.text[ 0 : current_index + 1 ] = [" "] *  (current_index + 1) # space
                inter_converted.styles[ 0 : current_index + 1 ] = [self.default_sgr_attributes] *  (current_index + 1) # default
                
            case 2:
                # If n is 2, clear entire line.
                inter_converted.clear()

            case _:
                raise RuntimeError()


        return inter_converted

    def parse_ed(self, sequence, inter_converted, current_index, parsed_screen, current_line_index):
        """Parse "Erase in Display" sequence."""

        extracter = ParametersExtractor()
        parameter = extracter.extract_ed(sequence)

       
        match parameter:
            case 0:
                #  If n is 0 (or missing), clear from cursor to end of screen.
                # Cursor position does not change.
                parsed_screen = parsed_screen[0:current_line_index]
                
                inter_converted.text = inter_converted.text[ 0 : current_index ]
                inter_converted.styles = inter_converted.text[ 0 : current_index ]

            case 1:
                # If n is 1, clear from cursor to beginning of the screen. 
                # Cursor position does not change.
                parsed_screen[0:current_line_index + 1 ] = [converter.InterConverted()] * (current_line_index + 1) # as newline

                inter_converted.text[ 0 : current_index + 1 ] = [" "] *  (current_index + 1)
                inter_converted.styles[ 0 : current_index + 1 ] = [self.default_sgr_attributes] *  (current_index + 1)
                
            case 2:
                # If n is 2, clear entire screen (and moves cursor to upper left on DOS ANSI.SYS). 
                raise RuntimeError()

            case 3:
                # If n is 3, clear entire screen and delete all lines saved in the scrollback buffer 
                raise NotImplementedError()

            case _:
                raise RuntimeError()

        
        return inter_converted , parsed_screen

    def parse_cup(self, sequence, inter_converted, current_index, parsed_screen, current_line_index):
        """Parse "Cursor Position" sequence."""

        extracter = ParametersExtractor()
        parameter = extracter.extract_cup(sequence)
        
        
        # Moves the cursor to row n, column m. The values are 1-based.
        next_line_index = parameter[0] - 1
        next_index = parameter[1] - 1
        
        # append current line to screen
        max_line_index = len(parsed_screen) - 1
        if current_line_index > max_line_index:
            # add new
            parsed_screen.append( inter_converted )
        else:
            # overwrite 
            parsed_screen[current_line_index] = inter_converted

        # Fill empty lines (including current).
        max_line_index  = len(parsed_screen) - 1
        need = next_line_index - max_line_index
        if need > 0:
            parsed_screen.extend( [converter.InterConverted()] * need )

        # move cursor
        inter_converted = parsed_screen[next_line_index]

        current_index = next_index
        current_line_index = next_line_index

        return inter_converted, current_index , parsed_screen , current_line_index


class StringParser:
    """Only parse SGR sequences and text."""

    def __init__(self , string) -> None:

        self.raw_string = string
        self.current_sgr_attributes = { "style":set() , "background":"" , "foreground":"" }
        
    def __parse_str_only(self) :
        
        csi_checker = CSIChecker()
        parsed_str = ""

        # splited_positions = split_by_ansi(self.ansi_escape_str)
        splited_sequences = split_by_ansi(self.raw_string)
        
        for sequence_str in splited_sequences:

            if not csi_checker.is_csi(sequence_str):
                parsed_str += sequence_str
                
        
        return parsed_str
        
    def __parse(self) :

        csi_checker = CSIChecker()
        sequence_parser = SequenceParser()
        
        inter_converted = converter.InterConverted()
        current_index = 0
        

        splited_sequences = split_by_ansi(self.raw_string)
        for sequence_str in splited_sequences:

            # Select Graphic Rendition
            if csi_checker.is_sgr_sequence(sequence_str):
                self.current_sgr_attributes = sequence_parser.parse_sgr(sequence_str , self.current_sgr_attributes)

            # text
            elif not csi_checker.is_csi(sequence_str):
                inter_converted , current_index = sequence_parser.parse_text( sequence_str , inter_converted , self.current_sgr_attributes , current_index )


        return inter_converted
       

    def to_string(self) -> str:

        return self.__parse_str_only()

    def to_html(self) -> str:

        inter_converted = self.__parse()
        html_tag = converter.to_html(inter_converted)
        
        return str(html_tag)


class ScreenParser:

    def __init__(self , screen_height=24 ) -> None:

        self.screen_buffer = deque()
        self.screen_height = screen_height

        self.current_sgr_attributes = { "style":set() , "background":"" , "foreground":"" }

        self.last_screen_finish = False

    def __split_by_newline(self, string: str) -> list:
        
        return string.splitlines()
    
    def __split_to_screen(self , string ) :
        """Split string to screen by '\x1B[2J'."""
        
        results = re.split( re_pattern.erase_display_clear_screen , string )

        # Remove empty strings from the results of re.split
        results = list(filter(None, results))

        # return [string] if there is no ed sequence.
        return results

    def __put_new_screen(self , raw_lines ) -> None:
        
        self.last_screen_finish = False
        self.screen_buffer.append(raw_lines)

    def __put_last_screen(self , raw_lines ) -> None:

        last_screen = self.screen_buffer[-1]
        last_screen.append(raw_lines)
        
    def __parse_str_only(self) :

        csi_checker = CSIChecker()
        parsed_screen = []
        
        raw_screen = self.screen_buffer.popleft()
        for raw_line in raw_screen:

            parsed_line = ""

            # parse line
            splited_sequences = split_by_ansi(raw_line)
            for sequence_str in splited_sequences:

                if not csi_checker.is_csi(sequence_str):
                    parsed_line += sequence_str

            # 
            parsed_screen.append( parsed_line )


        return parsed_screen

    def __parse_line(self, raw_line, parsed_screen, current_line_index):
      
        csi_checker = CSIChecker()
        sequence_parser = SequenceParser()

        inter_converted = converter.InterConverted()
        current_index = 0
        

        splited_sequences = split_by_ansi(raw_line)
        for sequence_str in splited_sequences:

            # Select Graphic Rendition
            if csi_checker.is_sgr_sequence(sequence_str):
                self.current_sgr_attributes = sequence_parser.parse_sgr(sequence_str, self.current_sgr_attributes)

            # text
            elif not csi_checker.is_csi(sequence_str):
                inter_converted , current_index = sequence_parser.parse_text( sequence_str , inter_converted , self.current_sgr_attributes , current_index  )

            # Erase in Line
            elif csi_checker.is_el_sequence(sequence_str):
                inter_converted = sequence_parser.parse_el( sequence_str , inter_converted , current_index )

            # Erase in Display
            elif csi_checker.is_ed_sequence(sequence_str):
                inter_converted, parsed_screen = sequence_parser.parse_ed(sequence_str, inter_converted, current_index, parsed_screen, current_line_index)

            # Cursor Position
            elif csi_checker.is_cup_sequence(sequence_str):
                inter_converted, current_index, parsed_screen, current_line_index = sequence_parser.parse_cup(sequence_str, inter_converted, current_index, parsed_screen, current_line_index)

        # 
        return inter_converted , parsed_screen , current_line_index

    def __parse(self) :
        
        current_line_index = 0
        parsed_screen = []
        
        raw_screen = self.screen_buffer.popleft()
        for raw_line in raw_screen:

            parsed_line, parsed_screen, current_line_index = self.__parse_line(raw_line, parsed_screen, current_line_index)

            max_line_index = len(parsed_screen) - 1
            if current_line_index > max_line_index:
                # add new
                parsed_screen.append( parsed_line )
            else:
                # overwrite 
                parsed_screen[current_line_index] = parsed_line

            current_line_index += 1


        return parsed_screen

    
    def put(self , string ) -> None:
        """Add new strings to the screen parser."""

        raw_screens = self.__split_to_screen(string)
        for raw_screen in raw_screens:

            raw_lines = self.__split_by_newline(raw_screen)

            if raw_screen == "\x1B[2J":
                # Consider 'clear entire screen' as the finish.
                self.last_screen_finish = True

            elif (self.last_screen_finish or 
                not self.screen_buffer):
                # Create a new screen if the last screen finishes or the buffer is empty.
                self.__put_new_screen(raw_lines)
         
            else:
                self.__put_last_screen(raw_lines)

    def to_string(self) -> str:
        
        if not self.screen_buffer:
            raise RuntimeError("no screen to convert")

        return self.__parse_str_only()

    def to_html(self) -> str:

        if not self.screen_buffer:
            raise RuntimeError("no screen to convert")

        parsed_screen = self.__parse()

        html_lines = []
        for parsed_line in parsed_screen:
            
            html_tag = converter.to_html(parsed_line)
            html_lines.append( html_tag ) 

        screen_html = converter.html_lines_to_screen(html_lines)

        return str(screen_html)

    def full(self) -> bool:
        """if current screen full """
        
        # empty or size >= screen_height
        if ( self.screen_buffer and
            len(self.screen_buffer[0]) >= self.screen_height
        ): 
            return True
        else:
            return False

    def finished(self) -> bool:
        """if current screen is finished"""

        # has next screen
        if len(self.screen_buffer) >= 2 :
            return True
        else:
            return False

