# Getting started

## Initialize a `ScreenParser`
要開始解析 [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)，我們需要先初始化一個 ScreenParser。


### 從新的 Screen 開始 :
```python
import ansiparser

ansip_screen = ansiparser.new_screen()
```


### 從已經轉譯的 `parsed_screen` 初始化 :
```python
import ansiparser
# ...
parsed_screen = old_ansip_screen.get_parsed_screen()

ansip_screen = ansiparser.from_screen(parsed_screen)
```


## 加入想轉譯的文字
完成初始化後，我們可以使用 `put()`，多次對 `ScreenParser` 加入想轉譯的文字。

```python
ansip_screen.put("\x1b[1;6H-World!")
ansip_screen.put("\x1b[1;1HHello")
```


## 解析
開始解析吧!

```python
ansip_screen.parse()
```

## 輸出
你可以依照你的需求，輸出你想要的形式，如格式化文字(使用 `list()` 儲存)或 HTML 等。

```python
converted_str = ansip_screen.to_formatted_string()
print(converted_str) # ['Hello-World!']

converted_html = ansip_screen.to_html()
print(converted_html) 
# <div class="line"><span class="">Hello-World!</span></div>
```






