"""fuzzyboa: a Pythonic FuzzBall-like MUCK server"""

class Server:
    """This class encompasses the running of a MUCK."""

    def configure(self, *args, **kwargs):
        """Ready the server for operation.

        This method must interpret the command line and any
        available config files, load or connect to the
        world database, and prepare the network listeners
        for operation.
        """
        pass #FIXME: Actually implement this method!

    def operate(self):
        """Serve the MUCK."""
        pass #FIXME: Actually implement this method!

    def shutdown(self):
        """Perform a clean shutdown of the server.

        This method causes the server to refuse new
        connections, disconnect existing clients, update
        config files, and save the world database.
        """
        pass #FIXME: Actually implement this method!

def mainentry():
    """Run a MUCK server.

    This function parses the command line and takes
    appropriate action. Generally that means creating a
    ``Server`` instance, passing the parsed-out
    command-line arguments to its ``configure`` method,
    then calling its ``operate`` and ``shutdown`` methods.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='A Pythonic MUCK server modelled on FuzzBall.'
        )
    #FIXME: Define commandline arguments.
    args = parser.parse_args()

    ser = Server()
    #FIXME: Map args to configure method args
    ser.operate()
    ser.shutdown()

#Let's make this runnable via python3 -m, not just the wrapper
if __name__ == '__main__':
    mainentry()
