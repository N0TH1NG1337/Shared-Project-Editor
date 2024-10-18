# User Interface .py

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

from user_interface.scene       import c_scene
from user_interface.widgets     import *


UI_BACK_COLOR: list = [ color( 203, 185, 213 ),
                        color( 253, 231, 236 ),
                        color( 156, 140, 182 ),
                        color( 224, 205, 224 )
]


class c_ui:
    """
        User Interface application class.

        main handle for application.
    """

    _application:   any             # GLFW Window

    _render:        c_render        # Main render object
    _impl:          GlfwRenderer    # Impl render backend

    _scenes:        list            # Attached scenes
    _active_scene:  int             # Active scene

    _events:        dict            # Events handler
    _data:          dict            # Application private data

    _last_error:    str             # Last application error

    def __init__( self ):
        """
            First set up for application
        """

        # Application handle must be at first None
        self._application       = None

        # Create render object
        self._render            = c_render( )

        # Set up scenes data
        self._scenes            = [ ]
        self._active_scene      = 0

        self._last_error        = ""

    # region : Window 

    def initialize( self, title: str, position: vector, size: vector ) -> bool:
        """
            Set up GLFW, Window applicaiton.
        """

        if not self.__init_glfw( ):
            return False

        self._data = { }

        self._data[ "position" ]  = position
        self._data[ "size" ]      = size
        self._data[ "title" ]     = title

        if not self.__init_window( ):
            return False
        
        if not self.__init_backend( ):
            return False
        
        # Prepare to save font objects and images
        self._data[ "fonts" ]   = { }
        self._data[ "images" ]  = { }

        # Success
        return True
        
    @safe_call( None )    
    def __init_glfw( self ) -> bool:
        """
            Load GLFW
        """

        if not glfw.init( ):
            self._last_error = "Failed to initialize OpenGL context"

            return False
        
        return True
    
    @safe_call( None )    
    def __init_window( self ) -> bool:
        """
            Create GLFW Window
        """

        # Set up glfw window hints
        glfw.window_hint( glfw.CONTEXT_VERSION_MAJOR,   3 )                             # Context related staff
        glfw.window_hint( glfw.CONTEXT_VERSION_MINOR,   3 )                             # Context related staff
        glfw.window_hint( glfw.OPENGL_PROFILE,          glfw.OPENGL_CORE_PROFILE )      # OpenGl related staff
        glfw.window_hint( glfw.OPENGL_FORWARD_COMPAT,   gl.GL_TRUE )                    # OpenGl related staff
        
        # Save localy 
        local_size: vector  = self._data[ "size" ].copy( )
        local_title: str    = self._data[ "title" ]

        # Create window
        self._application = glfw.create_window( local_size.x, local_size.y, local_title, None, None )

        # Validate
        if not self._application:
            glfw.terminate( )

            self._last_error = "Could not initialize Application"
            return False
        
        glfw.make_context_current( self._application )

        local_position: vector = self._data[ "position" ].copy()
        glfw.set_window_pos( self._application, local_position.x, local_position.y )

        # We dont need this data anymore
        del self._data[ "position" ]
        del self._data[ "size" ]
        del self._data[ "title" ]

        # Success on creating window
        return True

    @safe_call( None )    
    def __init_backend( self ) -> bool:
        """
            Set up imgui context and OpenGL renderer backend
        """

        imgui.create_context( )

        self._impl = GlfwRenderer( self._application, False )

        return True

    # endregion

    # region : Assets 

    @safe_call( None )
    def create_font( self, index: str, path: str, size: int ) -> any:
        """
            Create new font object
        """

        io = imgui.get_io( )

        # Supports :
        #   - English 32 - 126 (basic)
        #   - Russian 1024 - 1279
        #   - Hebrew  1424 - 1535
        # can support more just didn't have time to check everything
        from_english_to_hebrew_range = imgui.core.GlyphRanges( [ 32, 1535, 0 ] )

        # Create font from file
        new_font = io.fonts.add_font_from_file_ttf( path, size, None, from_english_to_hebrew_range )
        io.fonts.get_tex_data_as_rgba32( )

        # Save it
        fonts: dict = self._data[ "fonts" ]
        fonts[ index ] = new_font

        self._impl.refresh_font_texture( )

        return new_font
    
    @safe_call( None )
    def create_image( self, index: str, path: str, size: vector ) -> c_image | None:
        """
            Create new image object
        """

        new_img = c_image( )
        new_img.load( path, size )

        images: dict = self._data[ "images" ]
        images[ index ] = new_img

        return new_img

    def font( self, index: str ) -> any:
        """
            Access font by index
        """

        fonts: dict = self._data[ "fonts" ]

        if not index in fonts:
            return None
        
        
        return fonts[ index ]
    
    def image( self, index: str ) -> any:
        """
            Access image by index
        """

        images: dict = self._data[ "images" ]

        if not index in images:
            return None
        
        return images[ index ]
    
    # endregion

    # region : Scenes

    def new_scene( self ) -> c_scene:
        """
            Create and returns new scene object
        """

        new_scene: c_scene = c_scene( self )

        # Push back our new scene
        self._scenes.append( new_scene )

        # Looks strange, but we just save the current scene index in it
        new_scene.index( self._scenes.index( new_scene ) )

        return new_scene
    
    def active_scene( self, new_index: int = None ) -> c_scene:
        """
            Returns the active scene ptr.
            used mainly to change input handle between different scenes.

            but can also be used to check what is being currently displayed for the user
        """

        if new_index is None:
            return self._scenes[ self._active_scene ]
        
        self._active_scene = math.clamp( new_index, 0, len( self._scenes ) )
    
    def next_scene( self ) -> None:
        """
            Moves to the next scene
        """

        self._active_scene = math.clamp( self._active_scene + 1, 0, len( self._scenes ) )

    def previous_scene( self ) -> None:
        """
            Moves to the previous scene
        """

        self._active_scene = math.clamp( self._active_scene - 1, 0, len( self._scenes ) )
        
    # endregion
    
    # region : Events

    def initialize_events( self ) -> None:
        """
            Initialize events and set them up.

            warning ! call before .run()
        """

        self._events = { }

        # General application events
        self._events[ "pre_draw" ]          = c_event( )
        self._events[ "post_draw" ]         = c_event( )
        self._events[ "unload" ]            = c_event( )

        # User inpit events
        self._events[ "keyboard_input" ]    = c_event( )
        self._events[ "char_input" ]        = c_event( )
        self._events[ "mouse_position" ]    = c_event( )
        self._events[ "mouse_input" ]       = c_event( )
        self._events[ "mouse_scroll" ]      = c_event( )

        # Application's window events
        self._events[ "window_resize" ]     = c_event( )
        self._events[ "window_position" ]   = c_event( )
        self._events[ "window_maximize" ]   = c_event( )

        glfw.set_key_callback(              self._application, self.__event_keyboard_input )
        glfw.set_char_callback(             self._application, self.__event_char_input )
        glfw.set_cursor_pos_callback(       self._application, self.__event_mouse_position )
        glfw.set_mouse_button_callback(     self._application, self.__event_mouse_input )
        glfw.set_scroll_callback(           self._application, self.__event_mouse_scroll )
        glfw.set_window_size_callback(      self._application, self.__event_window_resize )
        glfw.set_window_pos_callback(       self._application, self.__event_window_position )
        glfw.set_window_maximize_callback(  self._application, self.__event_window_maximize )

        # Register that we done initializing events
        self._data[ "is_events_initialize" ] = True

    def __event_keyboard_input( self, window, key, scancode, action, mods ) -> None:
        """
            Keyboard input callback.

            receives :  window ptr  - GLFW Window
                        key         - GLFW Key
                        scancode    - GLFW Scan code
                        action      - GLFW Action
                        mods        - To be honest I have no idea what is this for
        """

        self.active_scene( ).event_keyboard_input( window, key, scancode, action, mods )

        event: c_event = self._events[ "keyboard_input" ]

        event + ( "window",      window )
        event + ( "key",         key )
        event + ( "scancode",    scancode )
        event + ( "action",      action )
        event + ( "mods",        mods )

        event.invoke( )

    def __event_char_input( self, window, char ) -> None:
        """
            Char input callback.

            receives :  window ptr  - GLFW Window
                        char        - char code
        """

        self.active_scene( ).event_char_input( window, char )

        event: c_event = self._events[ "char_input" ]

        event + ( "window",      window )
        event + ( "char",        char )

        event.invoke( )

    def __event_mouse_position( self, window, x, y ) -> None:
        """
            Mouse position change callback

            receives :  window ptr  - GLFW Window
                        x           - x-axis of mouse position
                        y           - y-axis of mouse position
        """

        self.active_scene( ).event_mouse_position( window, x, y )

        event: c_event = self._events[ "mouse_position" ]

        event + ( "window",      window )
        event + ( "x",           x )
        event + ( "y",           y )

        event.invoke( )

    def __event_mouse_input( self, window, button, action, mods ) -> None:
        """
            Mouse buttons input callback

            receives :  window ptr  - GLFW Window
                        button      - Mouse button
                        action      - Button action
                        mods        - no idea
        """

        self.active_scene( ).event_mouse_input( window, button, action, mods )

        event: c_event = self._events[ "mouse_input" ]

        event + ( "window",      window )
        event + ( "button",      button )
        event + ( "action",      action )
        event + ( "mods",        mods )

        event.invoke( )

    def __event_mouse_scroll( self, window, x_offset, y_offset ) -> None:
        """
            Mouse scroll input callback

            receives :  window ptr  - GLFW Window
                        x_offset    - x-axis of mouse wheel change (?)
                        y_offset    - y-axis of mouse wheel change (?)
        """

        self.active_scene( ).event_mouse_scroll( window, x_offset, y_offset )

        event: c_event = self._events[ "mouse_scroll" ]

        event + ( "window",      window )
        event + ( "x_offset",    x_offset )
        event + ( "y_offset",    y_offset )

        event.invoke( )

    def __event_window_resize( self, window, width, height ) -> None:
        """
            Window resize callback

            receives :  window ptr  - GLFW Window
                        width       - new width of window
                        height      - new height of window
        """

        event: c_event = self._events[ "window_resize" ]

        event + ( "window",      window )
        event + ( "width",       width )
        event + ( "height",      height )

        event.invoke( )

    def __event_window_position( self, window, x_pos, y_pos ) -> None:
        """
            Window position change callback.
            relative to the top left corner of the monitor it displayed on

            receives :  window ptr  - GLFW Window
                        x_pos       - x-axis position of the monitor
                        y_pos       - y-axis position of the monitor
        """

        event: c_event = self._events[ "window_position" ]

        event + ( "window",      window )
        event + ( "x_pos",       x_pos )
        event + ( "y_pos",       y_pos )

        event.invoke( )

    def __event_window_maximize( self, window, maximized ) -> None:
        """
            Window maximized or not callback

            receives :  window ptr  - GLFW Window
                        maximized   - is window maximized or not
        """

        event: c_event = self._events[ "window_maximize" ]

        event + ( "window",      window )
        event + ( "maximized",   maximized )

        event.invoke( )

    def set_event( self, event_index: str, function: any, function_name: str) -> bool:
        """
            Register function to a specific event
        """

        if not event_index in self._events:
            self._last_error = "Invalid Event Name"

            return False
        
        event: c_event = self._events[ event_index ]
        event.set(function, function_name, True)

        return True

    # endregion

    # region : Run Time

    def run( self ) -> None:
        """
            Main application window loop
        """

        if not self._application:
            raise Exception( "Failed to find application window. make sure you have first called .create_window()" )
        
        if not "is_events_initialize" in self._data:
            raise Exception( "Failed to verify events initialize. make sure you have first called .initialize_events() before .run()" )
        
        while not glfw.window_should_close( self._application ):
            # Process window events
            self.__process_input( )

            # Create new frame
            self.__pre_new_frame( )

            # Update our render
            self._render.update( )

            # MAIN STAFF HERE
            self.__draw_background( )
            self.__draw_scenes( )

            # Clear color buffer
            self.__clean_buffer( )

            # Complete creation of new frame
            self.__post_new_frame( )

            # Swap buffers
            glfw.swap_buffers( self._application )

        
        # Exit application
        self.__unload( )

    def __draw_background( self ) -> None:
        """
            Render background for application
        """

        size: vector = self.get_window_size( )
        self._render.gradiant(
            vector( ), size, 
            UI_BACK_COLOR[ 0 ],
            UI_BACK_COLOR[ 1 ],
            UI_BACK_COLOR[ 2 ],
            UI_BACK_COLOR[ 3 ]
        )

    def __draw_scenes( self ) -> None:
        """
            Draw all scenes
        """

        for scene in self._scenes:
            scene: c_scene = scene

            scene.show( scene.index( ) == self._active_scene )
            scene.draw( )

    def __process_input( self ) -> None:
        """
            Pulls and process window events and input
        """

        glfw.poll_events( )
        self._impl.process_inputs( )

    def __pre_new_frame( self ) -> None:
        """
            Before .new_frame was called
        """

        event: c_event = self._events[ "pre_draw" ]
        event + ( "ui", self )

        event.invoke( )

        imgui.new_frame( )

    def __post_new_frame( self ) -> None:
        """
            After new frame was done, render it
        """

        imgui.render( )
        self._impl.render( imgui.get_draw_data( ) )

        event: c_event = self._events[ "post_draw" ]
        event + ( "ui", self )

        event.invoke( )

    def __clean_buffer( self ) -> None:
        """
            Clears color buffer
        """

        gl.glClearColor( 1, 1, 1, 1 )
        gl.glClear( gl.GL_COLOR_BUFFER_BIT )

    def __unload( self ) -> None:
        """
            Application unload function
        """

        event: c_event = self._events[ "unload" ]
        event + ( "ui", self )

        event.invoke( )

        self._impl.shutdown( )
        glfw.terminate( )

    # endregion 

    def get_window_size( self ) -> vector:
        """
            Returns draw place size of window (Not windows top bar)
        """

        return vector( ).raw( glfw.get_window_size( self._application ) )

    def __call__( self, index: str ) -> any:
        if index == "last error":
            return self._last_error
        
        if index == "active scene":
            return self.active_scene( )
        
        if index in self._events:
            return self._events[ index ]
        
        return None

