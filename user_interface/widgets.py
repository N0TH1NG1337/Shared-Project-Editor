# User Interface Widgets .py

import OpenGL.GL as gl
import glfw
import imgui
import time

from sdk.color                  import color
from sdk.vector                 import vector
from sdk.math_operations        import math
from sdk.safe                   import safe_call
from sdk.image                  import c_image
from sdk.event                  import c_event

from user_interface.render      import c_render
from user_interface.animation   import c_animations


DEFAULT_SPEED   = 10
INVALID         = -1

COLOR_BUTTON_BACK   = color( 253, 231, 236 )
COLOR_BUTTON_ICON   = color( 156, 140, 182 )
COLOR_INPUT_BACK    = color( 253, 231, 236 )
COLOR_INPUT_ICON    = color( 156, 140, 182 )
COLOR_INPUT_TEXT    = color( 156, 140, 182 )
COLOR_INPUT_PONTER  = color( 156, 140, 182 )


class c_icon_button:
    """
        Button with icon class
    """

    _parent:        any             # c_scene parent 
    _index:         int             # button index

    _position:      vector          # current button position
    _size:          int             # current button size

    _icon:          c_image         # image object

    _callback:      any             # Button on press callback

    _render:        c_render        # parents render instance
    _animations:    c_animations    # current button animations handle
    
    # Private button data
    _is_hovered:    bool            # Is button hovered

    def __init__( self, parent: any, icon: c_image, position: vector, size: int, callback: any = None ):
        """
            Create new button instance
        """

        self._parent        = parent
        self._index         = INVALID

        self._position      = position.copy( )
        self._size          = size

        self._icon          = icon

        self._render        = self._parent.render( )
        self._animations    = c_animations( )

        self._callback = callback

        # Finish set up process
        self.__complete_attach( )
        self.__complete_setup( )

    def __complete_attach( self ) -> None:
        """
            Complete attach of current button to its parent
        """

        # Attach this element instance
        self._index = self._parent.attach_element( self )

        # Attach input events 
        self._parent.set_event( "mouse_position", self.__event_mouse_position, f"ButtonIcon::{ self._index }" )
        self._parent.set_event( "mouse_input", self.__event_mouse_input, f"ButtonIcon::{ self._index }" )

    def __complete_setup( self ) -> None:
        """
            Set up all the data for the button
        """

        self._is_hovered = False

        self._animations.prepare( "Background", 50 )
        self._animations.prepare( "Underline", 0 )

    # region : Render

    def draw( self, fade: float ) -> None:
        """
            Button main draw function
        """

        self.__draw_animations( )

        background = self._animations.value( "Background" )
        underline = self._animations.value( "Underline" )
        
        self._render.rect( self._position, self._position + self._size, COLOR_BUTTON_BACK.alpha_override(background) * fade, 10 )
        self._render.rect( 
            vector( self._position.x + self._size / 2 - 10, self._position.y + self._size - 6 ),
            vector( self._position.x + self._size / 2 + 10, self._position.y + self._size - 2 ),

            COLOR_BUTTON_ICON.alpha_override(underline) * fade,
            2
        )

        self._render.image( self._icon, self._position + self._size / 2 - self._icon.size( ) / 2, COLOR_BUTTON_ICON * fade )

    def __draw_animations( self ) -> None:
        """
            Do the animations process
        """

        self._animations.update( )

        self._animations.preform( "Background", self._is_hovered and 150 or 50, DEFAULT_SPEED )
        self._animations.preform( "Underline", self._is_hovered and 255 or 0, DEFAULT_SPEED )
    
    def position( self, new_position: vector = None ) -> vector | None:
        """
            Updates / returns current button position
        """

        if new_position is None:
            return self._position
        
        self._position.x = new_position.x
        self._position.y = new_position.y

    # endregion

    # region : Input 

    def __event_mouse_position( self, event ) -> None:
        """
            Mouse Position change callback
        """

        x = event( "x" )
        y = event( "y" )

        mouse_position = vector( x, y )

        self._is_hovered = mouse_position.is_in_bounds( self._position, self._size, self._size )

    def __event_mouse_input( self, event ) -> None:
        """
            Mouse buttons input callback
        """

        if not self._is_hovered:
            return
        
        button = event( "button" )
        if not button == glfw.MOUSE_BUTTON_LEFT:
            return
        
        action = event( "action" )
        if not action == glfw.PRESS:
            return
        
        if self._callback is not None:
            self._callback( )

    # endregion

class c_icon_text_button:
    """
        Button with icon and text class
    """

    _parent:        any             # c_scene parent 
    _index:         int             # button index

    _position:      vector          # current button position
    _size:          int             # current button size

    _icon:          c_image         # image object
    _font:          any             # Button font for text
    _text:          str             # Button text

    _callback:      any             # Button on press callback

    _render:        c_render        # parents render instance
    _animations:    c_animations    # current button animations handle
    
    # Private button data
    _is_hovered:    bool            # Is button hovered
    _text_size:     vector          # Button text size

    def __init__( self, parent: any, icon: c_image, font: any, text: str, position: vector, size: int, callback: any = None ):
        """
            Create new button instance
        """

        self._parent        = parent
        self._index         = INVALID

        self._position      = position.copy( )
        self._size          = size

        self._icon          = icon
        self._font          = font
        self._text          = text

        self._render        = self._parent.render( )
        self._animations    = c_animations( )

        self._callback      = callback

        # Finish set up process
        self.__complete_attach( )
        self.__complete_setup( )

    def __complete_attach( self ) -> None:
        """
            Complete attach of current button to its parent
        """

        # Attach this element instance
        self._index = self._parent.attach_element( self )

        # Attach input events 
        self._parent.set_event( "mouse_position", self.__event_mouse_position, f"ButtonIcon::{ self._index }" )
        self._parent.set_event( "mouse_input", self.__event_mouse_input, f"ButtonIcon::{ self._index }" )

    def __complete_setup( self ) -> None:
        """
            Set up all the data for the button
        """

        self._is_hovered    = False
        self._text_size     = vector( )

        self._animations.prepare( "Background", 50 )
        self._animations.prepare( "Underline", 0 )
        self._animations.prepare( "Width", self._size )

    # region : Render

    def draw( self, fade: float ) -> None:
        """
            Button main draw function
        """

        self.__draw_animations( )

        # Get animations values
        background          = self._animations.value( "Background" )
        width               = self._animations.value( "Width" )
        underline           = self._animations.value( "Underline" )
        
        # 1 Time calculate vectors
        start_position      = self._position
        end_position        = self._position + vector(width, self._size)

        self._render.rect( start_position, end_position, COLOR_BUTTON_BACK.alpha_override(background) * fade, 10 )

        self._render.rect( 
            vector( self._position.x + width / 2 - 10, self._position.y + self._size - 6 ),
            vector( self._position.x + width / 2 + 10, self._position.y + self._size - 2 ),

            COLOR_BUTTON_ICON.alpha_override(underline) * fade,
            2
        )

        self._render.image( self._icon, self._position + self._size / 2 - self._icon.size( ) / 2, COLOR_BUTTON_ICON * fade )

        self._render.push_clip_rect( start_position, end_position )
        self._render.text( 
            self._font, 
            self._position + vector( 
                self._size, 
                self._size / 2 - self._text_size.y / 2 
            ), 
            COLOR_BUTTON_ICON * fade, 
            self._text 
        )
        self._render.pop_clip_rect( )

    def __draw_animations( self ) -> None:
        """
            Do the animations process
        """

        self._animations.update( )

        self._text_size: vector = self._render.measure_text( self._font, self._text )

        self._animations.preform( "Background", self._is_hovered and 150                                    or 50,          DEFAULT_SPEED )
        self._animations.preform( "Width",      self._is_hovered and self._size + self._text_size.x + 12    or self._size,  DEFAULT_SPEED )
        self._animations.preform( "Underline",  self._is_hovered and 255                                    or 0,           DEFAULT_SPEED )
    
    def position( self, new_position: vector = None ) -> vector | None:
        """
            Updates / returns current button position
        """

        if new_position is None:
            return self._position
        
        self._position.x = new_position.x
        self._position.y = new_position.y

    # endregion

    # region : Input 

    def __event_mouse_position( self, event ) -> None:
        """
            Mouse Position change callback
        """

        x = event( "x" )
        y = event( "y" )

        mouse_position      = vector( x, y )

        width               = self._animations.value( "Width" )
        self._is_hovered    = mouse_position.is_in_bounds( self._position, width, self._size )

    def __event_mouse_input( self, event ) -> None:
        """
            Mouse buttons input callback
        """

        if not self._is_hovered:
            return
        
        button = event( "button" )
        if not button == glfw.MOUSE_BUTTON_LEFT:
            return
        
        action = event( "action" )
        if not action == glfw.PRESS:
            return
        
        if self._callback is not None:
            self._callback( )

    # endregion

class c_text_input:
    """
        Single line text input class
    """

    _parent:            any
    _index:             int

    _position:          vector
    _size:              vector  # (x. text field width, y. height)

    _icon:              c_image
    _font:              any
    _text:              str
    _input:             str     # Text Input value

    _render:        c_render        # parents render instance
    _animations:    c_animations    # current button animations handle

    # Private button data
    _is_hovered:        bool 
    _is_typing:         bool
    _is_ctrl:           bool
    _is_password:       bool

    _text_size:         vector
    _input_size:        vector
    _mouse_position:    vector
    _click_delta:       int
    _input_index:       int
    _input_offset:      float

    _time:              int

    def __init__( self, parent: any, icon: c_image, font: any, text: str, position: vector, size: vector ):
        """
            Create new button instance
        """

        self._parent        = parent
        self._index         = INVALID

        self._position      = position.copy( )
        self._size          = size.copy( )

        self._icon          = icon
        self._font          = font
        self._text          = text
        self._input         = ""

        self._render        = self._parent.render( )
        self._animations    = c_animations( )

        self._time = time.time()

        # Finish set up process
        self.__complete_attach( )
        self.__complete_setup( )

    def __complete_attach( self ) -> None:
        """
            Complete attach of current button to its parent
        """

        # Attach this element instance
        self._index = self._parent.attach_element( self )

        # Attach events
        self._parent.set_event( "mouse_position",   self.__event_mouse_position,    f"TextInput::{ self._index }" )
        self._parent.set_event( "mouse_input",      self.__event_mouse_input,       f"TextInput::{ self._index }" )
        self._parent.set_event( "char_input",       self.__event_char_input,        f"TextInput::{ self._index }" )
        self._parent.set_event( "keyboard_input",   self.__event_keyboard_input,    f"TextInput::{ self._index }" )
        
    def __complete_setup( self ) -> None:
        """
            Set up all the data for the button
        """

        # Add the Icon box width
        self._size.x            = self._size.x + self._size.y

        self._is_hovered        = False
        self._is_ctrl           = False
        self._is_typing         = False
        self._is_password       = False

        self._text_size         = vector( )
        self._input_size        = vector( )
        self._mouse_position    = vector( )
        self._click_delta       = INVALID

        self._input_index       = 0
        self._input_offset      = self._position.x + self._size.y + 5

        self._animations.prepare( "Background", 0 )
        self._animations.prepare( "TextAlpha",  255 )
        self._animations.prepare( "Underline",  10 )
        self._animations.prepare( "InputWidth", self._size.y )
        self._animations.prepare( "PointerShow", 0 )


    def input_type( self, is_password: bool = None ) -> bool | None:
        """
            Returns / Sets if the current text input should be for password
        """

        if is_password is None:
            return self._is_password
        
        self._is_password = is_password

    def get( self ) -> str:
        """
            Returns current input value
        """

        return self._input
    
    # region : Render

    def draw( self, fade: float ) -> None:
        """
            Button main draw function
        """

        self.__draw_animations( )

        background          = self._animations.value( "Background" )
        background_width    = self._animations.value( "InputWidth" )
        text_alpha          = self._animations.value( "TextAlpha" )
        underline           = self._animations.value( "Underline" )
        
        self._render.rect( self._position, self._position + vector( background_width, self._size.y ), COLOR_INPUT_BACK.alpha_override(background) * fade, 10 )
        self._render.rect( 
            vector( self._position.x + self._size.y - 6, self._position.y + self._size.y / 2 - underline ),
            vector( self._position.x + self._size.y - 2, self._position.y + self._size.y / 2 + underline ),

            COLOR_INPUT_ICON * fade,
            2
        )

        self._render.image( self._icon, self._position + vector(self._size.y, self._size.y) / 2 - self._icon.size( ) / 2, COLOR_INPUT_ICON * fade )

        if text_alpha > 0:
            self._render.text( 
                self._font, 
                vector( 
                    self._position.x + self._size.y + 5, 
                    self._position.y + self._size.y / 2 - self._text_size.y / 2 
                ),
                COLOR_INPUT_TEXT.alpha_override( text_alpha ) * fade,
                self._text
            )
        
        # Some pre made calculations
        correct_input           = self.correct_text( self._input )
        correct_input_by_index  = self.correct_text( self._input[ :self._input_index ] )
        correct_size            = self._render.measure_text( self._font, correct_input )
        correct_by_index_size   = self._render.measure_text( self._font, correct_input_by_index )

        start_clip  = self._position + vector(self._size.y + 5, 0)
        end_clip    = self._position + vector( background_width - 10, self._size.y )

        self._render.push_clip_rect( start_clip, end_clip )

        self.__draw_input( fade, correct_input )
        self.__draw_index( fade, correct_input_by_index, correct_by_index_size )

        self._render.pop_clip_rect( )

        self.__preform_correct_offset( vector( end_clip.x, start_clip.x ), correct_by_index_size )
        self.__preform_set_index( correct_input )

    def __draw_input( self, fade: float, text: str ) -> None:
        """
            Draw Input text
        """
        
        self._render.text( 
            self._font, 
            vector( self._input_offset, self._position.y + self._size.y / 2 - self._text_size.y / 2 ),
            COLOR_INPUT_TEXT * fade,
            text
        )


    def __draw_index( self, fade: float, text: str, text_size: vector ) -> None:
        """
            Draw the select index pointer
        """
        pointer_alpha = self._animations.value( "PointerShow" )

        if not self._is_typing and pointer_alpha == 0:
            return
        
        start_y_offset = self._position.y + self._size.y / 2 - self._text_size.y / 2
        
        self._render.rect( 
            vector( self._input_offset + text_size.x, start_y_offset - 2 ),
            vector( self._input_offset + text_size.x + 1, start_y_offset + (2 + text_size.y) * pointer_alpha ),
            COLOR_INPUT_PONTER * fade * pointer_alpha
        )

    def __preform_correct_offset( self, end_clip: vector, text_size: vector ) -> None:
        """
            Preform some calculations for text offset for clip
        """

        if not self._is_typing:
            return
        
        set_offset = self._input_offset + text_size.x + 1

        # Move the text left / right to focus on the index to be in visible area
        if set_offset > end_clip.x:
            self._input_offset -= set_offset - end_clip.x

        if ( set_offset - 1 ) < end_clip.y:
            self._input_offset += end_clip.y - ( set_offset - 1 )

    def __preform_set_index( self, text: str ) -> None:
        """
            Preform calculations on user press on text
        """

        if not self._is_typing:
            return

        if self._click_delta == INVALID:
            return
        
        selected_index: int     = 0
        input_width:    float   = 0.0

        while selected_index < len( text ):
            width = self._render.measure_text( self._font, text[ selected_index ] ).x

            if input_width + ( width * 0.5 ) > self._click_delta:
                break

            input_width += width
            selected_index += 1

        self._click_delta = INVALID
        self._input_index = selected_index

    def correct_text( self , text: str ) -> str:
        """
            If is password is True, conver the text into password type
        """

        if self._is_password:
            return "*" * len( text )
        
        return text

    def __draw_animations( self ) -> None:
        """
            Do the animations process
        """

        self._animations.update( )

        if self._is_typing:
            self._animations.preform( "Background", 200, DEFAULT_SPEED )
        elif self._is_hovered:
            self._animations.preform( "Background", 100, DEFAULT_SPEED )
        else:
            self._animations.preform( "Background", 50, DEFAULT_SPEED )

        if self._is_typing:
            self._animations.preform( "PointerShow", 1, DEFAULT_SPEED )
            self._animations.preform( "Underline", ( self._size.y - 6 ) / 2, DEFAULT_SPEED )
        else:
            self._animations.preform( "PointerShow", 0, DEFAULT_SPEED )
            self._animations.preform( "Underline", 10, DEFAULT_SPEED )

        if not self._is_typing and self._input == "":
            self._animations.preform( "InputWidth", self._size.y + self._text_size.x + 10, DEFAULT_SPEED )
            self._animations.preform( "TextAlpha", 200, DEFAULT_SPEED )
        else:
            self._animations.preform( "TextAlpha", 0, DEFAULT_SPEED )
            self._animations.preform( "InputWidth", self._size.x, DEFAULT_SPEED )

        self._text_size = self._render.measure_text( self._font, self._text )

    def position( self, new_position: vector = None ) -> vector | None:
        """
            Updates / returns current button position
        """

        if new_position is None:
            return self._position
        
        self._position.x = new_position.x
        self._position.y = new_position.y

    # endregion

    # region : Input

    def insert( self, text: str  ) -> None:
        """
            Inserts specific text into selected index
        """

        self._input = self._input[ :self._input_index ] + text + self._input[ self._input_index: ]
        self._input_index += len( text )

    def pop( self ) -> str | None:
        """
            Pops char from input in selected index
        """

        if self._input_index == 0:
            return None
        
        char = self._input[ self._input_index - 1 ]

        self._input = self._input[ :self._input_index - 1 ] + self._input[ self._input_index: ]
        self._input_index -= 1

        return char

    def __event_mouse_position( self, event ) -> None:
        """
            Mouse Position change callback
        """

        x = event( "x" )
        y = event( "y" )

        self._mouse_position.x = x
        self._mouse_position.y = y

        self._is_hovered = self._mouse_position.is_in_bounds( self._position, self._animations.value( "InputWidth" ), self._size.y )

    def __event_mouse_input( self, event ) -> None:
        """
            Mouse buttons input callback
        """
        
        button = event( "button" )
        action = event( "action" )

        if button != glfw.MOUSE_BUTTON_LEFT or action != glfw.PRESS:
            return

        if not self._is_hovered:
            self._is_typing = False
            return
        
        if not self._is_typing:
            self._is_typing = True

        #self._click_position = self._mouse_position.copy( )
        self._click_delta = self._mouse_position.x - self._input_offset

    def __event_char_input( self, event ) -> None:
        """
            Captures what char was pressed
        """

        if not self._is_typing:
            return
        
        char = chr( event( "char" ) )

        self.insert( char )

    def __event_keyboard_input( self, event ) -> None:
        """
            General keyboard input handle
        """

        if not self._is_typing:
            return
        
        key         = event( "key" )
        action      = event( "action" ) 

        self.__ctrl_handle( key, action )

        if action == glfw.PRESS:
            self.__repeat_handle( key )

            self.__paste_handle( key )

            if key == glfw.KEY_ENTER:
                self._is_typing = False

        if action == glfw.REPEAT:
            self.__repeat_handle( key )


    def __ctrl_handle( self, key, action ):
        """
            Exception capture for Ctrl key input
        """

        if key != glfw.KEY_LEFT_CONTROL and key != glfw.KEY_RIGHT_CONTROL:
            return

        if action == glfw.PRESS:
            self._is_ctrl = True

        if action == glfw.RELEASE:
            self._is_ctrl = False

    def __repeat_handle( self, key ):
        """
            Executable input handle for PRESS and REPEAT calls
        """

        # Remove
        if key == glfw.KEY_BACKSPACE:
            self.pop( )

        # Move index left
        if key == glfw.KEY_LEFT and self._input_index > 0:
            self._input_index -= 1

        # Move index right
        if key == glfw.KEY_RIGHT and self._input_index < len( self._input ):
            self._input_index += 1

    def __paste_handle( self, key ):

        if not self._is_ctrl:
            return

        if key != glfw.KEY_V:
            return

        result: bytes = glfw.get_clipboard_string( None )
        result: str = result.decode( )

        self.insert(result)

    # endregion
