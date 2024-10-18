# Project in Cyber.

## Shared code editor
version : [0.1]

requirements:

- window 10 or newer
- python version : 3.7 or newer

- python libraries
```python
pip install imgui[full]
pip install numpy
pip install pillow
```


## Change Log
```txt
date : 16/10/2024

| action        | name                  | type      | description
- Added         c_text_input            class       a single line text input
- Changed       c_render.measure_text   function    now each string size will be devided to sum of all chars
- Changed       c_render.text           function    now each char will render differently and together a string
- Changed       c_render.gradient_text  function    now the function pushes only one time font, and uses default imgui render
- Removed       c_ui.refrash_textures   function    no need, since every new font created will call it
- Changed       c_ui.create_font        function    now each new font create, _impl.refresh_font_texture will be called
```
