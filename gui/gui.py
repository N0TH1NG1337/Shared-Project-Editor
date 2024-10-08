"""
    Project :
        gui and widgets classes

    change log [08/10/2024]:

    road map :
    [] - add buttons
        [x] - create base
        [] - add button draw
        [] - add button interact options
        [] - complete button animations

    [] - add single line text input
        [] - create base
        [] - add text input draw
        [] - add text input simple interactions
        [] - add clip for text input
        [] - add option to change insert point in text
        [] - add final interactions
        [] - complete animations

    [] - create pop up windows on application

    [] - create nav bar
        [] - add background for nav bar (not sure)
        [] - add navbar buttons
        [] - add for buttons window popup

    [] - add file options {save}
    [] - add settings option {exit}
    [] - add text editor
        [] - think
    [] - add button with images
    [] - add notifications
"""

# region : Includes

from imgui.integrations.glfw import GlfwRenderer
import OpenGL.GL as gl
import numpy as np
import glfw
import imgui
import sys

from gui_types import color, vector, event, clamp, safe_call
from gui_render import c_render, c_animations, c_image

# endregion


# region : Constants

INVALID: int = -1
GUI_BACK_COLOR: list = [color(203, 185, 213),
                        color(253, 231, 236),
                        color(156, 140, 182),
                        color(224, 205, 224)]

GUI_BUTTON_BACK_COLOR: color = color()


# endregion


# region : Widgets

class c_button:
    """
        Regular button object to attach to c_scene
    """

    _parent:    any     # Scene ptr
    _position:  vector  # Button position
    _size:      vector  # Button render size

    _id:        str     # Button ID in scene
    _text:      str     # Text to render on the button
    _font:      any     # Font object to render

    _callback:  any     # Callback function on button press
    # looks like this gets executed in the middle of a frame. if we want to do staff after
    # need to find other solutions
    # Option 1 : create delay call .
    # Option 2 : create queue of callbacks before / on / after render frame

    _animations:    c_animations    # Button animations
    _info:          dict            # Button additional shared information

    def __init__(self,
                 parent: any,           # c_scene instance
                 id: str,               # current id in scene
                 text: str,             # current text on the button
                 font: any,             # font for the text
                 position: vector,      # position of the button in the scene
                 size: vector,          # size of the button
                 callback: any = None   # function to execute on button press
                 ):
        """
            Initialize button object
        """

        # Set parent
        self._parent = parent

        # Set button's vectors
        self._position = position
        self._size = size

        self._id = id
        self._text = text
        self._font = font

        # Set up (even if empty) callback on press
        self._callback = callback

        # Create animations handle
        self._animations = c_animations()

        # Create dict to store additional information about button
        self._info = {}

        # Complete button set up
        self.__setup()

    def __setup(self):
        """
            Set up all the keys for possible values for info dict
            and cache animations values
        """

        self._info["is_hovered"] = False

        self._animations.cache("hovered", 0)
        self._animations.cache("text_color", color())

    # region : Button Draw

    def draw(self, fade: float):
        """
            Draw button.
        """

        self.__handle_animations()

        scene: c_scene = self._parent
        render: c_render = scene.render()

        # TODO ! Draw button here

    def __handle_animations(self):
        """
            All button animations handle
        """

        # Local scene and render values
        scene: c_scene = self._parent
        render: c_render = scene.render()

        # Update animations interpolation
        self._animations.update(render.get_frame_time())

    def position(self, new_position: vector = None):
        """
            Update / returns position value
        """

        if new_position is None:
            return self._position

        self._position.x = new_position.x
        self._position.y = new_position.y

    # endregion

    # region : Button interaction

    def mouse_position(self, event):
        """
            Used to capture mouse position
        """

        x_axis = event("x")
        y_axis = event("y")

        mouse_pos = vector(x_axis, y_axis)
        self._info["is_hovered"] = mouse_pos.is_in_bounds(self._position, self._size.x, self._size.y)

    def mouse_buttons(self, event):
        """
            Used to capture mouse buttons actions for the button
        """

        pass

    # endregion


class c_text_input:
    pass


# endregion


# region : Scenes

class c_scene:
    _gui:           any  # Parent
    _index:         int  # Current index in queue

    _show:          bool  # Should show scene
    _events:        dict  # Scene events
    _ui:            dict  # Scene UI Elements

    _render:        c_render        # Scene render functions
    _animations:    c_animations    # Scene animations functions

    def __init__(self, parent):

        # Set current parent
        self._gui = parent

        # Set scene data
        self._index = INVALID
        self._show = False

        # Set up UI handle dict
        self._ui = {}

        self.__initialize_events()
        self.__initialize_draw()

    # region : Draw scene

    def __initialize_draw(self):
        """
            Create render object and animations handler object
        """

        self._render = c_render()
        self._animations = c_animations()

        # Cache scene fade
        self._animations.cache("Fade", 0)

    def draw(self):
        """
            Draw function for scene.
            called each frame
        """

        # Update render information and animations
        self._render.update()
        self._animations.update(self._render.get_frame_time())

        # Preform global fade animation
        fade = self._animations.preform("Fade", self._show and 1 or 0, 6)

        # Draw each ui element
        for id in self._ui:
            item = self._ui[id]
            item.draw(fade)

        # Call draw event
        self._events["draw"] + ("scene", self)
        self._events["draw"]()

    # endregion

    # region : Widgets attach

    def add_button(self, id: str, text: str, font: any, position: vector, size: vector, callback: any = None):
        """
            Create a new button object and attach it to the scene.
        """

        new_button = c_button(self, id, text, font, position, size, callback)
        self._ui[id] = new_button

        # attach here all the callbacks
        self.register_event("mouse_pos", new_button.mouse_position, f"Button:{id}")
        self.register_event("mouse_buttons", new_button.mouse_buttons, f"Button:{id}")

        return new_button

    def add_text_input(self, id: str, text: str, position: vector, size: vector):
        """
            Create a new single line input and attach it to the scene
        """

        pass

    # endregion

    # region : Interaction with parent

    def index(self, value: int = None):
        """
            Returns / Updates index value
        """

        if value is None:
            return self._index

        # Not recommended since scenes are statically ordered in gui buffer
        self._index = value

    def show(self, value: bool = None):
        """
            Returns / Updates if the scene should show
        """

        if value is None:
            return value

        self._show = value

    def gui(self):
        """
            Returns a ptr to this scene parent
        """

        return self._gui

    def render(self) -> c_render:
        return self._render

    def animations(self) -> c_animations:
        return self._animations

    def ui(self, id: str):
        if id in self._ui:
            return self._ui[id]

        return None

    # endregion

    # region : Scene callbacks and events

    def __initialize_events(self):
        """
            Initialize events
        """

        self._events = {
            "draw": event(),

            "keyboard": event(),
            "char": event(),
            "mouse_pos": event(),
            "mouse_buttons": event(),
            "scroll": event()
        }

    def keyboard_callback(self, window, key, scancode, action, mods):
        """
            Keyboard input callback.
            receives :  window ptr  - GLFW Window
                        key         - GLFW Key
                        scancode    - GLFW Scan code
                        action      - GLFW Action
                        mods        - To be honest I have no idea what is this for
        """

        self._events["keyboard"] + ("window", window)
        self._events["keyboard"] + ("key", key)
        self._events["keyboard"] + ("scancode", scancode)
        self._events["keyboard"] + ("action", action)
        self._events["keyboard"] + ("mods", mods)

        self._events["keyboard"]()

    def char_callback(self, window, char):
        """
            Char input callback.
            very useful for text input.

            Instead of using keyboard callback, with scancode and more information.
        """

        self._events["char"] + ("window", window)
        self._events["char"] + ("char", char)

        self._events["char"]()

    def mouse_pos_callback(self, window, x, y):
        """
            Mouse position change callback
        """

        self._events["mouse_pos"] + ("window", window)
        self._events["mouse_pos"] + ("x", x)
        self._events["mouse_pos"] + ("y", y)

        self._events["mouse_pos"]()

    def mouse_buttons(self, window, button, action, mods):
        """
            Mouse buttons input callback
        """

        self._events["mouse_buttons"] + ("window", window)
        self._events["mouse_buttons"] + ("button", button)
        self._events["mouse_buttons"] + ("action", action)
        self._events["mouse_buttons"] + ("mods", mods)

        self._events["mouse_buttons"]()

    def scroll_callback(self, window, x_offset, y_offset):
        """
            Mouse scroll input callback
        """

        self._events["scroll"] + ("window", window)
        self._events["scroll"] + ("x_offset", x_offset)
        self._events["scroll"] + ("y_offset", y_offset)

        self._events["scroll"]()

    def register_event(self, event_type, function, name):
        """
            Register function to a specific event
        """

        self._events[event_type] + (function, name, True)

    # endregion


# endregion


# region : GUI

class c_gui:
    """
        Graphical User Interface class.

        this will behave as our base for application.
        most operations will be done here

        this GUI window will work in a scene way
    """

    _application:   any             # GLFW Window

    _render:        c_render        # Regular render staff
    _impl:          GlfwRenderer    # Impl render backend

    _scenes:        list            # Scenes queue
    _active_scene:  int             # Active Scene index in queue

    _events:        dict            # GUI events
    _data:          dict            # GUI shared data

    _last_error:    str             # Last error GUI has caught

    def __init__(self):
        """
            Constructor for GUI object
        """

        # Application handle must be at first None
        self._application = None

        # Events handle must be initialized
        # before since there are different kinds of events
        self._events = {}

        # last error :)
        self._last_error = ""

        # Render functions
        self._render = c_render()

        # Scenes part
        self._scenes = []       # Use list as queue
        self._active_scene = 0  # Scene that will be input handled

    def last_error(self):
        """
            Returns last occurred error
        """

        return self._last_error

    # region : Window creation and set up

    def create_window(self, title: str, position: vector, size: vector) -> bool:
        """
            Will be as our main function to create window
        """

        # Set up share data dictionary
        self._data = {}

        # Try to load GLFW context
        if not self.__init_glfw():
            return False

        # Populate our shared data with information
        self._data["position"] = position
        self._data["size"] = size
        self._data["title"] = title

        # Try to create application window
        if not self.__init_window():
            return False

        if not self.__init_backend():
            return False

        # prepare for asset creation
        self._data["fonts"] = {}
        self._data["images"] = {}

        # Success window creation
        return True

    def __init_glfw(self) -> bool:
        """
            Init GLFW
        """

        if not glfw.init():
            self._last_error = "Failed to initialize OpenGL context"
            return False

        return True

    def __init_window(self) -> bool:
        """
            Create and saves window to our application
        """

        # Set up glfw window hints
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)  # Context related staff
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)  # Context related staff
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)  # OpenGl related staff
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)  # OpenGl related staff

        # Save locally for faster access
        local_size: vector = self._data["size"].copy()
        local_title: str = self._data["title"]

        # Create window
        self._application = glfw.create_window(local_size.x, local_size.y, local_title, None, None)

        # Check if valid
        if not self._application:
            # Failed to create window. Release glfw
            glfw.terminate()
            self._application = None

            self._last_error = "Could not initialize Application"
            return False

        # Set current context
        glfw.make_context_current(self._application)

        # Set start window position
        position: vector = self._data["position"].copy()
        glfw.set_window_pos(self._application, position.x, position.y)

        # TODO ! CLEAR SIZE, TITLE AND POSITION SINCE WE DONT NEED THEM ANYMORE
        # del self._data["title"]
        # del self._data["size"]
        # del self._data["position"]

        return True

    @safe_call(None)
    def __init_backend(self) -> bool:
        """
            Set up Imgui context and create impl instance
        """

        # Create ImGUI context
        imgui.create_context()

        # the attach_callbacks arguments was hidden on the start
        # and I almost lost my mind, trying to understand why I cant attach callbacks in glfw
        self._impl = GlfwRenderer(self._application, False)

        return True

    def load_assets(self):
        """
            Function to call after we set up to load every asset that will be used
        """

        # Must refresh textures in order to load them correctly
        self._impl.refresh_font_texture()

    @safe_call(None)
    def create_font(self, index, path, size) -> bool:
        """
            Create and save new font object to render text
        """

        io = imgui.get_io()

        #   Supports :
        #   - English 32 - 126 (basic)
        #   - Russian 1024 - 1279
        #   - Hebrew  1424 - 1535
        # can support more just didn't have time to check everything
        from_english_to_hebrew_range = imgui.core.GlyphRanges([32, 1535, 0])

        # Create font and attach support for english - hebrew glyphs
        new_font = io.fonts.add_font_from_file_ttf(path, size, None, from_english_to_hebrew_range)
        io.fonts.get_tex_data_as_rgba32()

        fonts_dict: dict = self._data["fonts"]
        fonts_dict[index] = new_font

        return True

    @safe_call(None)
    def create_image(self, index: str, path: str, size: vector) -> bool:
        """
            Create and save new image object to render images later
        """

        new_img = c_image()
        new_img.load(path, size)

        images_dict: dict = self._data["images"]
        images_dict[index] = new_img

        return True

    # endregion

    # region : Scenes part

    def create_scene(self) -> c_scene:
        """
            Creates and attaches new scene to the GUI
        """

        # Create new scene
        new_scene: c_scene = c_scene(self)

        # Push back to the queue
        self._scenes.append(new_scene)

        # Nonsense but works
        # Save current scene index in queue
        new_scene.index(self._scenes.index(new_scene))

        # Return created scene for use
        return new_scene

    def active_scene(self) -> c_scene:
        """
            Returns the active scene ptr.
            used mainly to change input handle between different scenes.

            but can also be used to check what is being currently displayed for the user
        """

        return self._scenes[self._active_scene]

    def next_scene(self) -> None:
        """
            Moves to the next scene
        """

        # TODO ! ADD LIMIT CHECKS
        # if we will try to call this function on last scene we will run into exception
        self._active_scene += 1

    def previous_scene(self) -> None:
        """
            Moves to the previous scene
        """

        # TODO ! ADD LIMIT CHECKS
        # if we will try to call this function on last scene we will run into exception
        self._active_scene -= 1

    # endregion

    # region : Run Time

    def run(self):
        """
            Main application window loop
        """

        # Check if everything was set upped before
        if not self._application:
            raise Exception("Failed to find application window. make sure you have first called .create_window()")

        if "is_events_initialize" not in self._data:
            raise Exception("Failed to verify events initialize. make sure you have first called .initialize_events() "
                            "before .run()")

        # Run application loop
        while not glfw.window_should_close(self._application):

            # Process and prepare for new frame
            self.__process_input()
            self.__pre_new_frame()

            # Must update render before use each frame
            self._render.update()

            # DO STAFF HERE
            self.__draw_background()
            self.__draw_scenes()

            # After done rendering new frame clear color buffer
            self.__clear_view_target()

            # After clearing and rendering swap buffers
            self.__post_new_frame()
            glfw.swap_buffers(self._application)

        # If we exit the loop, it's meaning that the application is closed
        self.__unload()

    def __process_input(self):
        """
            Pulls and process window events and input
        """

        glfw.poll_events()
        self._impl.process_inputs()

    def __pre_new_frame(self):
        """
            Before .new_frame was called
        """

        self._events["pre_draw"] + ("gui", self)
        self._events["pre_draw"]()

        imgui.new_frame()

    def __clear_view_target(self):
        """
            Clears view target and color buffer
        """

        gl.glClearColor(1, 1, 1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def __post_new_frame(self):
        """
            After new frame was done, render it
        """

        imgui.render()
        self._impl.render(imgui.get_draw_data())

        self._events["post_draw"] + ("gui", self)
        self._events["post_draw"]()

    def __unload(self):
        """
            Application unload function
        """

        self._events["unload"] + ("gui", self)
        self._events["unload"]()

        self._impl.shutdown()
        glfw.terminate()

    def __draw_background(self):
        """
            Render background for application
        """

        size = self.get_window_size()
        self._render.gradiant(vector(), size,
                              GUI_BACK_COLOR[0],
                              GUI_BACK_COLOR[1],
                              GUI_BACK_COLOR[2],
                              GUI_BACK_COLOR[3])

    def __draw_scenes(self):
        """
            Draw all scenes based on active scene index
        """

        for scene in self._scenes:
            scene: c_scene = scene  # Just fast localize for easier access

            scene.show(scene.index() == self._active_scene)
            scene.draw()

    # endregion

    # region : Events and callbacks

    def initialize_events(self):
        """
            Initialize events and set them up.

            warning ! call before .run()
        """

        # General events
        self._events["pre_draw"] = event()      # Before new frame was declared
        self._events["post_draw"] = event()     # After frame was complete but before buffer swap
        self._events["unload"] = event()        # On application unload

        # User input events
        self._events["keyboard"] = event()  #
        self._events["char_input"] = event()
        self._events["mouse_pos"] = event()
        self._events["mouse_buttons"] = event()
        self._events["mouse_scroll"] = event()

        # Application's window events
        self._events["window_size"] = event()
        self._events["window_pos"] = event()
        self._events["window_max"] = event()

        # Set up glfw callbacks
        glfw.set_key_callback(self._application, self.__keyboard_callback)
        glfw.set_char_callback(self._application, self.__char_callback)
        glfw.set_cursor_pos_callback(self._application, self.__mouse_pos_callback)
        glfw.set_mouse_button_callback(self._application, self.__mouse_buttons)
        glfw.set_scroll_callback(self._application, self.__scroll_callback)
        glfw.set_window_size_callback(self._application, self.__window_size_callback)
        glfw.set_window_pos_callback(self._application, self.__window_pos_callback)
        glfw.set_window_maximize_callback(self._application, self.__window_max_callback)

        self._data["is_events_initialize"] = True

    def __keyboard_callback(self, window, key, scancode, action, mods):
        """
            Keyboard input callback.
            receives :  window ptr  - GLFW Window
                        key         - GLFW Key
                        scancode    - GLFW Scan code
                        action      - GLFW Action
                        mods        - To be honest I have no idea what is this for
        """

        self.active_scene().keyboard_callback(window, key, scancode, action, mods)

        self._events["keyboard"] + ("window", window)
        self._events["keyboard"] + ("key", key)
        self._events["keyboard"] + ("scancode", scancode)
        self._events["keyboard"] + ("action", action)
        self._events["keyboard"] + ("mods", mods)

        self._events["keyboard"]()

    def __char_callback(self, window, char):
        """
            Char input callback.
        """

        self.active_scene().char_callback(window, char)

        self._events["char_input"] + ("window", window)
        self._events["char_input"] + ("char", char)

        self._events["char_input"]()

    def __mouse_pos_callback(self, window, x, y):
        """
            Mouse position change callback
        """

        self.active_scene().mouse_pos_callback(window, x, y)

        self._events["mouse_pos"] + ("window", window)
        self._events["mouse_pos"] + ("x", x)
        self._events["mouse_pos"] + ("y", y)

        self._events["mouse_pos"]()

    def __mouse_buttons(self, window, button, action, mods):
        """
            Mouse buttons input callback
        """

        self.active_scene().mouse_buttons(window, button, action, mods)

        self._events["mouse_buttons"] + ("window", window)
        self._events["mouse_buttons"] + ("button", button)
        self._events["mouse_buttons"] + ("action", action)
        self._events["mouse_buttons"] + ("mods", mods)

        self._events["mouse_buttons"]()

    def __scroll_callback(self, window, x_offset, y_offset):
        """
            Mouse scroll input callback
        """

        self.active_scene().scroll_callback(window, x_offset, y_offset)

        self._events["mouse_scroll"] + ("window", window)
        self._events["mouse_scroll"] + ("x_offset", x_offset)
        self._events["mouse_scroll"] + ("y_offset", y_offset)

        self._events["mouse_scroll"]()

    def __window_size_callback(self, window, width, height):
        """
            Window resize callback
        """

        self._events["window_size"] + ("window", window)
        self._events["window_size"] + ("width", width)
        self._events["window_size"] + ("height", height)

        self._events["window_size"]()

    def __window_pos_callback(self, window, x_pos, y_pos):
        """
            Window position change callback.
            relative to the top left corner of the monitor it displayed on
        """

        self._events["window_pos"] + ("window", window)
        self._events["window_pos"] + ("x_pos", x_pos)
        self._events["window_pos"] + ("y_pos", y_pos)

        self._events["window_pos"]()

    def __window_max_callback(self, window, maximized):
        """
            Window maximized or not callback
        """

        self._events["window_max"] + ("window", window)
        self._events["window_max"] + ("maximized", maximized)

        self._events["window_max"]()

    def register_event(self, event_type, function, name):
        """
            Register function to a specific event
        """

        self._events[event_type] + (function, name, True)

    # endregion

    # region : access GUI data

    def font(self, index) -> any:
        fonts_dict: dict = self._data["fonts"]
        return fonts_dict[index]

    def image(self, index) -> c_image:
        images_dict: dict = self._data["images"]
        return images_dict[index]

    # endregion

    # region : Window utils functions

    def get_window_size(self) -> vector:
        """
            Returns draw place size of window (Not windows top bar)
        """

        return vector().as_tuple(glfw.get_window_size(self._application))

    def maximize(self):
        """
            Set application window to be maximized
        """

        glfw.maximize_window(self._application)

    def exit(self):
        """
            Stop window render
        """

        glfw.set_window_should_close(self._application, True)

    # endregion


# endregion


"""
    This GUI works in a scene way
    
    the GUI contains a queue for scenes, (when starting up, the gui must contain at least 1 scene)
    all the scenes renders together, only the current scene with active index has any input handle.
    
    therefore any scene must handle the situation manually inside of it. (which already do that)
    Moreover, each scene can be used to populate the content directly. If its about events, render, input handle and more
    
    Each option to attach to scene something should be done before the main application run.
    (On paper possible also to attach mid run time but not recommended)
    
    In addition, each element will have a pointer to its parent:
    1. gui -> scene -> ui. 
    && 
    2. ui element -> scene -> gui
    
    Example:
    
    def draw_scene(event):
        scene: c_scene = event("scene")
        gui: c_gui = scene.gui()
        render: c_render = scene.render()
        animations: c_animations = scene.animations()
    
        fade = animations.value("Fade")
        render.text(gui.font("Title"), vector(50, 50), color(156, 140, 182) * fade, f"Shared Project")
    
    
    def main():
        gui = c_gui()
        gui.create_window("TEST WINDOW", vector(100, 100), vector(1050, 600))
        gui.create_font("Title", "C:\\Windows\\Fonts\\arialbd.ttf", 50)
    
        gui.load_assets()
        gui.initialize_events()
    
        scene: c_scene = gui.create_scene()
        scene.register_event("draw", draw_scene, "DrawSceneTest")
        
        scene2: c_scene = gui.create_scene()
    
        gui.run()
    
    
    if __name__ == "__main__":
        main()
    
    : End example
    
    Here we can see that the first scene 'scene' will be the first one.
    In the scene we can add condition or widget to move to the next.
    By the way, the transition animation is automated based on how the scene wants to do that :)
    * In some cases we can merge different scenes to be visible at once
"""
