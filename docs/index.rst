AnsiParser 
========================

|version| |pyversions| |licence|

.. |version| image:: https://img.shields.io/pypi/v/ansiparser?label=stable
   :target: https://pypi.org/project/ansiparser/#history

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/ansiparser
   :target: https://pypi.org/project/ansiparser

.. |licence| image:: https://img.shields.io/github/license/bubble-tea-project/ansiparser
   :target: https://github.com/bubble-tea-project/ansiparser/blob/main/LICENSE


| AnsiParser 是一個 library，用於解析 ANSI 跳脫序列（ANSI escape sequences），
| 它可以像 terminal 一樣處理這些序列並解析為螢幕輸出，支援將其轉換為格式化文字或 HTML 等。


以下是一個簡易的使用範例:

.. code-block:: python

   import ansiparser

   ansip_screen = ansiparser.new_screen()
   ansip_screen.put("\x1b[1;6H-World!\x1b[1;1HHello")

   ansip_screen.parse()
   converted = ansip_screen.to_formatted_string()

   print(converted) # ['Hello-World!']


讓我們開始吧! :doc:`Getting started <getting_started>`



.. toctree::
   :hidden:

   install
   getting_started
   reference/index





