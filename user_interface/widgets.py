# User Interface Widgets .py

import OpenGL.GL as gl
import glfw
import imgui

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

COLOR_BUTTON_BACK = color( 253, 231, 236 )
COLOR_BUTTON_ICON = color( 156, 140, 182 )


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

        render: c_render = self._parent.render( )

        background = self._animations.value( "Background" )
        underline = self._animations.value( "Underline" )
        
        render.rect( self._position, self._position + self._size, COLOR_BUTTON_BACK.alpha_override(background) * fade, 10 )
        render.rect( 
            vector( self._position.x + self._size / 2 - 10, self._position.y + self._size - 6 ),
            vector( self._position.x + self._size / 2 + 10, self._position.y + self._size - 2 ),

            COLOR_BUTTON_ICON.alpha_override(underline) * fade,
            2
        )

        render.image( self._icon, self._position + self._size / 2 - self._icon.size( ) / 2, COLOR_BUTTON_ICON * fade )

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

        # Save localy important data
        render: c_render    = self._parent.render( )

        # Get animations values
        background          = self._animations.value( "Background" )
        width               = self._animations.value( "Width" )
        underline           = self._animations.value( "Underline" )
        
        # 1 Time calculate vectors
        start_position      = self._position
        end_position        = self._position + vector(width, self._size)

        render.rect( start_position, end_position, COLOR_BUTTON_BACK.alpha_override(background) * fade, 10 )

        render.rect( 
            vector( self._position.x + width / 2 - 10, self._position.y + self._size - 6 ),
            vector( self._position.x + width / 2 + 10, self._position.y + self._size - 2 ),

            COLOR_BUTTON_ICON.alpha_override(underline) * fade,
            2
        )

        render.image( self._icon, self._position + self._size / 2 - self._icon.size( ) / 2, COLOR_BUTTON_ICON * fade )

        render.push_clip_rect( start_position, end_position )
        render.text( 
            self._font, 
            self._position + vector( 
                self._size, 
                self._size / 2 - self._text_size.y / 2 
            ), 
            COLOR_BUTTON_ICON * fade, 
            self._text 
        )
        render.pop_clip_rect( )

    def __draw_animations( self ) -> None:
        """
            Do the animations process
        """

        self._animations.update( )

        render:             c_render   = self._parent.render( )
        self._text_size:    vector     = render.measure_text( self._font, self._text )

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

    pass
