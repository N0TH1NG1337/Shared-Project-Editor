# SDK Event .py

class c_event:
    """
        Event object

        Very usefull to handle multiple functions that should be
        executed all at once with the same arguments.
    """

    _event_data:        dict    # Event shared data
    _event_function:    dict    # Event callbacks

    def __init__( self ):
        """
            Constructor for event object
        """

        # Setup event data handler
        self._event_data        = { }

        # Setup event functions handler
        self._event_functions   = { }

    def __get( self, index ) -> any:
        """
            Receive event's specific data.
            Called within event callbacks
        """

        if index in self._event_data:
            return self._event_data[ index ]

        return None

    def __add__( self, information: tuple ) -> None:
        """
            Adds new information to the event
        """

        self._event_data[ information[ 0 ] ] = information[ 1 ]

    def set( self, fn: any, index: str, allow_arguments: bool = True ) -> None:
        """
            Register new function for callback
        """

        self._event_functions[ index ] = {
            "call":         fn,
            "allow_args":   allow_arguments
        }

    def unset( self, index: str ) -> None:
        """
            Removes a specific function from callbacks
        """

        del self._event_function[ index ]

    def invoke( self ) -> None:
        """
            Execute the event and call all the functions
        """

        for function_name in self._event_functions:
            method_data = self._event_functions[ function_name ]

            # TODO ! maybe add safe call
            if method_data[ "allow_args" ]:
                method_data[ "call" ]( self.__get )
            else:
                method_data[ "call" ]( )

    def __call__( self ) -> None:
        """
            Execute the event and call all the functions
        """

        self.invoke( )