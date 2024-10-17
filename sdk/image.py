# SDK Image .py

import OpenGL.GL as gl
from PIL import Image
import numpy
import imgui

from sdk.vector import vector
from sdk.safe import safe_call

class c_image:
    """
        Image class
    """

    _id:    any     # Texture_Id for OPENGL
    _size:  vector  # Texture size

    def __init__( self ):

        self._id    = None
        self._size  = vector( )

    @safe_call(None)
    def load( self, path: str, size: vector ) -> None:
        """
            Loads image by path and size
        """

        # Attach wanted size
        self._size.x = size.x
        self._size.y = size.y

        # Open and get image data
        image           = Image.open( path )
        image_data      = numpy.array( image.convert( "RGBA" ), dtype=numpy.uint8 )

        # Generate OpenGL Texture Id
        self._id = gl.glGenTextures( 1 )

        # Bind Texture to id
        gl.glBindTexture( gl.GL_TEXTURE_2D, self._id )

        # Set parameters
        gl.glTexParameteri( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR )
        gl.glTexParameteri( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR )

        # Create and set texture
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_RGBA,
            self._size.x, self._size.y,
            0,
            gl.GL_RGBA,
            gl.GL_UNSIGNED_BYTE,
            image_data
        )

        # Return on success
        return True
    
    def size( self ) -> vector:
        """
            Get Image size
        """

        return self._size.copy( )
    
    def __call__( self ):
        """
            Get Image ID
        """
        return self._id
