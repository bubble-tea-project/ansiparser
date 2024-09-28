<h1 align="center">ansi-to-html</h1>

<div align="center">

A convenient library for converting ANSI escape sequences into text or HTML.


![GitHub last commit](https://img.shields.io/github/last-commit/bubble-tea-project/ansi-to-html) 
![GitHub License](https://img.shields.io/github/license/bubble-tea-project/ansi-to-html)

</div>

## 📖 Description
Parse ANSI escape sequences into screen outputs. This library implements a parser that processes escape sequences like a terminal, allowing you to convert them into formatted text or HTML.

## ✨ Supported Features
- CSI (Control Sequence Introducer) sequences
    - SGR (Select Graphic Rendition) 
    - CUP (Cursor Position)
    - ED (Erase in Display)
    - EL (Erase in Line)
- Convert
    - formatted text 
    - HTML

## 🎨 Usage
```python
import ansi_to_html

a2h_screen = ansi_to_html.new_screen()
a2h_screen.put("\x1b[1;6H-World!\x1b[1;1HHello")

a2h_screen.parse()
converted = a2h_screen.to_formatted_string()

print(converted) # ['Hello-World!']
```


## 📜 License
![GitHub License](https://img.shields.io/github/license/bubble-tea-project/ansi-to-html)







