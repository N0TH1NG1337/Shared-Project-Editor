# User Interface Scenes .py

import OpenGL.GL as gl
import glfw
import imgui

from imgui.integrations.glfw    import GlfwRenderer

from sdk.color                  import color
from sdk.vector                 import vector
from sdk.math_operations        import math
from sdk.safe                   import safe_call
from sdk.image                  import c_image
from sdk.event                  import c_event

from user_interface.render      import c_render
from user_interface.animation   import c_animations

SCENE_ANIMATION_SPEED: int = 10


class c_scene:

    _parent:        any     # c_ui instance
    _index:         int     # Current scene index in queue

    _show:          bool    # Should render this scene
    _events:        dict    # Current scene events
    _ui:            list    # Current scene ui items

    _render:        c_render        # Render handle
    _animations:    c_animations    # Animations handle

    def __init__( self, parent: any ):
        
        # Set parent. MUST HAVE
        self._parent    = parent

        # Draw information
        self._index     = -1
        self._show      = False

        # Create dict to save ui elements
        self._ui        = [ ]

        self.__initialize_draw( )
        self.__initialize_events( )

    # region : Draw

    def __initialize_draw( self ) -> None:
        """
            Set up default draw settings
        """

        self._render        = c_render( )
        self._animations    = c_animations( )

        # Cache simple animations data
        self._animations.prepare( "Fade", 0 )

    def draw( self ) -> None:
        """
            Draw function for scene.
            called each frame
        """

        self._render.update( )
        self._animations.update( )

        fade = self._animations.preform( "Fade", self._show and 1 or 0, SCENE_ANIMATION_SPEED )

        event: c_event = self._events[ "draw" ]
        event + ( "scene", self )
        event.invoke( )

        for item in self._ui:
            item.draw( fade )

    # endregion

    # region : Events

    def __initialize_events( self ) -> None:
        """
            Set up current scene events
        """

        self._events = { }

        self._events[ "draw" ] = c_event( )

        self._events[ "keyboard_input" ]    = c_event( )
        self._events[ "char_input" ]        = c_event( )
        self._events[ "mouse_position" ]    = c_event( )
        self._events[ "mouse_input" ]       = c_event( )
        self._events[ "mouse_scroll" ]      = c_event( )

    def event_keyboard_input( self, window, key, scancode, action, mods ) -> None:
        """
            Keyboard input callback.

            receives :  window ptr  - GLFW Window
                        key         - GLFW Key
                        scancode    - GLFW Scan code
                        action      - GLFW Action
                        mods        - To be honest I have no idea what is this for
        """

        event: c_event = self._events[ "keyboard_input" ]

        event + ( "window",      window )
        event + ( "key",         key )
        event + ( "scancode",    scancode )
        event + ( "action",      action )
        event + ( "mods",        mods )

        event.invoke( )

    def event_char_input( self, window, char ) -> None:
        """
            Char input callback.

            receives :  window ptr  - GLFW Window
                        char        - char code
        """

        event: c_event = self._events[ "char_input" ]

        event + ( "window",      window )
        event + ( "char",        char )

        event.invoke( )

    def event_mouse_position( self, window, x, y ) -> None:
        """
            Mouse position change callback

            receives :  window ptr  - GLFW Window
                        x           - x-axis of mouse position
                        y           - y-axis of mouse position
        """

        event: c_event = self._events[ "mouse_position" ]

        event + ( "window",      window )
        event + ( "x",           x )
        event + ( "y",           y )

        event.invoke( )

    def event_mouse_input( self, window, button, action, mods ) -> None:
        """
            Mouse buttons input callback

            receives :  window ptr  - GLFW Window
                        button      - Mouse button
                        action      - Button action
                        mods        - no idea
        """

        event: c_event = self._events[ "mouse_input" ]

        event + ( "window",      window )
        event + ( "button",      button )
        event + ( "action",      action )
        event + ( "mods",        mods )

        event.invoke( )

    def event_mouse_scroll( self, window, x_offset, y_offset ) -> None:
        """
            Mouse scroll input callback

            receives :  window ptr  - GLFW Window
                        x_offset    - x-axis of mouse wheel change (?)
                        y_offset    - y-axis of mouse wheel change (?)
        """

        event: c_event = self._events[ "mouse_scroll" ]

        event + ( "window",      window )
        event + ( "x_offset",    x_offset )
        event + ( "y_offset",    y_offset )

        event.invoke( )

    def set_event( self, event_index: str, function: any, function_name: str ) -> None:
        """
            Register new function for specific event
        """

        if not event_index in self._events:
            return
        
        event: c_event = self._events[ event_index ]
        event.set( function, function_name, True )
 
    # endregion

    # region : General

    def attach_element( self, item: any ) -> int:
        """
            Attach new element to this scene
        """

        self._ui.append( item )
        return self._ui.index( item )

    def index( self, new_value: int = None ) -> int:
        """
            Returns / Sets the current scene index in the queue
        """
        if new_value is None:
            return self._index
        
        self._index = new_value

    def show( self, new_value: bool = None ) -> bool:
        """
            Return / Sets if the scene should show
        """

        if new_value is None:
            return self._show
        
        self._show = new_value

    def parent( self ) -> any:
        """
            Returns current scene parent
        """

        return self._parent
    
    def render( self ) -> c_render:
        """
            Returns current scene render object
        """

        return self._render
    
    def animations( self ) -> c_animations:
        """
            Returns current scene animations handler
        """

        return self._animations
    
    def element( self, index: int ) -> any:
        """
            Returns specific element attached to this scene
        """

        if index in self._ui:
            return self._ui[ index ]
        
        return None

    # endregion
