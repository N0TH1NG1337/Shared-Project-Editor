"""
    Project :
        render wrap for imgui renderer

    change log [04/10/2024]:
    - moved each render function from points to vectors
    - create normalized linear function
    - removed option to load fonts / images {now controlled by gui}

"""

# region : Includes

import OpenGL.GL as gl
from PIL import Image
import numpy as np
import imgui

from gui_types import color, vector, linear

# endregion


class c_image:

    _id:    any     # Texture_Id for OPENGL
    _size:  vector  # Texture size

    def __init__(self):
        self._size = vector()
        self._id = None

    def load(self, path, size):
        self._size.x = size.x
        self._size.y = size.y

        image = Image.open(path)
        img_data = np.array(image.convert("RGBA"), dtype=np.uint8)

        self._id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._id)

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        gl.glTexImage2D(gl.GL_TEXTURE_2D,
                        0,
                        gl.GL_RGBA,
                        self._size.x, self._size.y,
                        0,
                        gl.GL_RGBA,
                        gl.GL_UNSIGNED_BYTE,
                        img_data
                        )

    def size(self) -> vector:
        return self._size.copy()

    def __call__(self) -> any:
        return self._id


class c_render:
    """
        Pure render functions.

        Wraps Imgui DrawList options with some other custom ones,
        Each function must be called each frame since the render type is immediate mode
    """

    _draw_list: any     # ImDrawList*
    _frame_time: float  # Frame time

    def __init__(self):
        """
            Constructor for render handle object
        """

        self._draw_list = None
        self._frame_time = 0

    def update(self) -> None:
        """
            Called every frame.
            since ImDrawList resets on each buffer swap, we need to get the new one
            + calculate frame time for interpolation
        """

        # Updates the drawlist
        self._draw_list = imgui.get_background_draw_list()

        # Calculate the frame time. Used for interpolation
        frame_rate = imgui.get_io().framerate
        if frame_rate != 0:
            self._frame_time = 1 / frame_rate

    def get_frame_time(self) -> float:
        """
            Returns frame time value
        """

        return self._frame_time

    def get_mouse_position(self) -> vector:
        """
            Returns a mouse position as vector
        """

        pos = imgui.get_io().mouse_pos
        return vector(pos.x, pos.y)

    # region : Draw things

    def push_clip_rect(self, position: vector, end_position: vector):
        """
            Push start vector and end vector to clip area,
            this will crop every render that is outside the rect area
        """

        self._draw_list.push_clip_rect(position.x, position.y, end_position.x, end_position.y)

    def pop_clip_rect(self):
        """
            Pops clip rect and restores everything else
        """

        self._draw_list.pop_clip_rect()

    def image(self, img: c_image, position: vector, clr: color, size: vector = None):
        """
            Renders Image in a specific place with specific size.
            recommended : use original size for the image while loading and while using
        """

        # If our size is None its mean we want to use the size
        # we declared when create the image
        if size is None:
            size = img.size()

        self._draw_list.add_image(img(), (position.x, position.y), (position.x + size.x, position.y + size.y), col=clr())

    def text(self, font, position: vector, clr: color, text: str, flags: str = ""):
        """
            Renders text with custom fond.
            can also use flags

            flags :
            - "c" will center the text
        """

        # Push font
        imgui.push_font(font)

        # Use to center text
        text_size = (0, 0)
        if 'c' in flags:
            text_size = imgui.calc_text_size(text)

        # Draw text
        self._draw_list.add_text(position.x - text_size[0] / 2, position.y - text_size[1] / 2, clr(), text)

        # Pop font
        imgui.pop_font()

        # Return text size if centered to use if need
        return text_size

    def gradient_text(self, font, position: vector, clr1: color, clr2: color, text: str):
        """
            Render gradient text.

            clr1 - start color,
            clr2 - end color

            waring : DO NOT RENDER 1 CHAR WITH THAT
        """

        # Besides fps killer function.
        # This looks dope

        # Extract values
        r1, g1, b1, a1 = clr1.unpack()
        r2, g2, b2, a2 = clr2.unpack()

        # Get text length
        string_len = len(text) - 1

        # Create a percentage that will be added for each char
        percentage = color(
            (r2 - r1) / string_len,
            (g2 - g1) / string_len,
            (b2 - b1) / string_len,
            (a2 - a1) / string_len
        )

        # Text pad to find where last char located
        text_pad = 0

        # Loop through each character
        for char in text:

            # Render each character
            self.text(font, position + vector(text_pad, 0), color(r1, g1, b1, a1), char)

            # Populate the pad for next cha
            text_pad = text_pad + self.measure_text(font, char).x

            # Change the color for the next char
            r1 = r1 + percentage.r
            g1 = g1 + percentage.g
            b1 = b1 + percentage.b
            a1 = a1 + percentage.a

    def measure_text(self, font, text: str) -> vector:
        """
            Measures and returns a vector of text size based on custom font.

            warning ! must be called on render event since sometimes the return values is zero vector
        """

        # TODO ! if the return vector is zero repeat until it fixed

        # Push font
        imgui.push_font(font)

        # Use calculate text size by Imgui (returns a tuple)
        text_size = imgui.calc_text_size(text)

        # Pop font
        imgui.pop_font()

        # Return size as vector
        return vector().as_tuple(text_size)

    def rect(self, position: vector, end_position: vector, clr: color, roundness: int = 0):
        """
            Render fulled rect.
        """

        self._draw_list.add_rect_filled(
            position.x, position.y,          # unpack the position 2d cords      [ignore .z]
            end_position.x, end_position.y,  # unpack the end position 2d cords  [ignore .z]
            clr(),                           # call color object to return ImColor u32 type
            rounding=roundness               # assignee rounding if need
        )

    def rect_outline(self, position: vector, end_position: vector, clr: color, thick: float = 1, roundness: int = 0):
        """
            Render outline rect.
        """

        self._draw_list.add_rect(
            position.x, position.y,             # unpack the position 2d cords      [ignore .z]
            end_position.x, end_position.y,     # unpack the end position 2d cords  [ignore .z]
            clr(),                              # call color object to return ImColor u32 type
            rounding=roundness,                 # assignee rounding if need
            thickness=thick                     # set outline thickness
        )

    def gradiant(self, position: vector, end_position: vector, clr_up_left: color, clr_up_right: color, clr_bot_left: color, clr_bot_right: color, roundness: int = 0):
        """
            Render gradient rect.

            with rounding option (Prefer not to animate size / position since there will be glitched with corners)
        """

        if roundness == 0:
            self._draw_list.add_rect_filled_multicolor(
                position.x, position.y,             # unpack the position 2d cords      [ignore .z]
                end_position.x, end_position.y,     # unpack the end position 2d cords  [ignore .z]
                clr_up_left(),                      # Convert Top Left color
                clr_up_right(),                     # Convert Top Right color
                clr_bot_right(),                    # Convert Bottom Right color
                clr_bot_left())                     # Convert Bottom Left color

        else:
            # Besides the pain...
            # works fine

            # FIXME ! (I am not sure if possible) when we more it, some pixels reset and doesnt register as corners

            # TODO ! Try to optimize the code, a lot of trash here

            # Calculate points for the corners
            corenr_tl_x = position.x + roundness
            corenr_tl_y = position.y + roundness

            corenr_tr_x = end_position.x - roundness
            corenr_tr_y = position.y + roundness

            corner_bl_x = position.x + roundness
            corner_bl_y = end_position.y - roundness

            corner_br_x = end_position.x - roundness
            corner_br_y = end_position.y - roundness

            # Render rounded corners
            self._draw_list.path_clear()
            self._draw_list.path_line_to(corenr_tl_x, corenr_tl_y)
            self._draw_list.path_arc_to_fast(corenr_tl_x, corenr_tl_y, roundness, 6, 9)
            self._draw_list.path_fill_convex(clr_up_left())

            self._draw_list.path_clear()
            self._draw_list.path_line_to(corenr_tr_x, corenr_tr_y)
            self._draw_list.path_arc_to_fast(corenr_tr_x, corenr_tr_y, roundness, 9, 12)
            self._draw_list.path_fill_convex(clr_up_right())

            self._draw_list.path_clear()
            self._draw_list.path_line_to(corner_bl_x, corner_bl_y)
            self._draw_list.path_arc_to_fast(corner_bl_x, corner_bl_y, roundness, 3, 6)
            self._draw_list.path_fill_convex(clr_bot_left())

            self._draw_list.path_clear()
            self._draw_list.path_line_to(corner_br_x, corner_br_y)
            self._draw_list.path_arc_to_fast(corner_br_x, corner_br_y, roundness, 0, 3)
            self._draw_list.path_fill_convex(clr_bot_right())

            # Render background
            self._draw_list.add_rect_filled_multicolor(corenr_tl_x, corenr_tl_y,
                                                       corner_br_x, corner_br_y,
                                                       clr_up_left(),
                                                       clr_up_right(),
                                                       clr_bot_right(),
                                                       clr_bot_left())

            # Render outline
            self._draw_list.add_rect_filled_multicolor(position.x, corenr_tl_y,
                                                       corenr_tl_x, corner_br_y,
                                                       clr_up_left(),
                                                       clr_up_left(),
                                                       clr_bot_left(),
                                                       clr_bot_left())

            self._draw_list.add_rect_filled_multicolor(corenr_tl_x, corner_bl_y,
                                                       corner_br_x, end_position.y,
                                                       clr_bot_left(),
                                                       clr_bot_right(),
                                                       clr_bot_right(),
                                                       clr_bot_left())

            self._draw_list.add_rect_filled_multicolor(corenr_tl_x, position.y,
                                                       corner_br_x, corenr_tl_y,
                                                       clr_up_left(),
                                                       clr_up_right(),
                                                       clr_up_right(),
                                                       clr_up_left())

            self._draw_list.add_rect_filled_multicolor(corner_br_x, corenr_tl_y,
                                                       end_position.x, corner_br_y,
                                                       clr_up_right(),
                                                       clr_up_right(),
                                                       clr_bot_right(),
                                                       clr_bot_right())

    def circle(self, position: vector, clr: color, radius: float, segments: int = 0):
        """
            Render circle.
        """

        self._draw_list.add_circle_filled(
            position.x, position.y,     # Unpack position
            radius,                     # Set radius
            clr(),                      # Convert color
            segments                    # Set segments [0 - auto segments calculation]
        )

    def circle_outline(self, position: vector, clr: color, radius: float, segments: int = 0, thickness: float = 1):
        """
            Render outline circle
        """

        self._draw_list.add_circle(
            position.x, position.y,     # Unpack position
            radius,                     # Set radius
            clr(),                      # Convert color
            segments,                   # Set segments
            thickness                   # Set outline thickness
        )

    def line(self, position: vector, end_position: vector, clr: color, thickness: float = 1):
        """
            Render line
        """
        self._draw_list.add_line(
            position.x, position.y,             # Unpack start position
            end_position.x, end_position.y,     # Unpack end position
            clr(),                              # Convert color
            thickness                           # Set line thickness
        )

    # endregion


class c_animations:
    """
        Animation handle object

        use to cache / preform animations,
        can use int / float / color / vector.
    """

    _animations_cache:  dict    # Animations values
    _interpolation:     float   # Animation's interpolation

    def __init__(self):
        """
            Constructor for animation handle
        """

        self._animations_cache: dict = {}
        self._interpolation = 0

    def update(self, value):
        """
            Must update interpolation each frame.
            In most cases the best option will be to use frame_time
        """

        self._interpolation = value

    def value(self, index: str, value: any = None):
        """
            Return / Update value based on index
        """

        # Check if we want to receive and not to update
        if value is None:
            return self._animations_cache[index]

        # Update
        self._animations_cache[index] = value

    def cache(self, index, value):
        """
            Cache value before start using it.
            can be called within a render callback but still not recommended
        """

        # Check if the index is new
        if index not in self._animations_cache:

            # If yes, create and set init value
            self._animations_cache[index] = value

    def preform(self, index: str, value: any, speed: int = 10, hold: float = 0.01) -> any:
        """
            Preform animation of specific index and return end value
        """

        # Get type
        value_type = type(value)

        # If its regular value type use linear(...)
        if value_type == float or value_type == int:
            self._animations_cache[index] = linear(self._animations_cache[index], value, speed * self._interpolation, hold)

        # If not it must be vector / color which have .lerp(...) option
        else:
            self._animations_cache[index] = self._animations_cache[index].lerp(value, speed * self._interpolation, hold)

        # Return end value
        return self._animations_cache[index]
