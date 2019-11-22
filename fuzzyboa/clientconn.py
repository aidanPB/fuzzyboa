"""
``clientconn``: Client connection management
============================================

.. module:: fuzzyboa.clientconn
    :synopsis: Classes for dealing with client connections.
.. moduleauthor:: Aidan Pitt-Brooke <f.sylvestris@gmail.com>

.. data:: NETWORK_NEWLINE

    A carriage return followed by a linefeed.
"""
#stdlib imports:
from enum import Enum, unique
from numbers import Real
from queue import Queue
import time
from typing import Optional
#third-party imports:
from telnetlib3 import TelnetReader, TelnetWriter
#sibling imports:
from . import world

__all__ = ('NETWORK_NEWLINE',
           'ConnState',
           'Connection',
           )

NETWORK_NEWLINE = "\r\n"

@unique
class ConnState(Enum):
    """The states a client connection can be in."""
    NORMAL = 1
    KICK_PENDING = 2
    #KICK_PENDING connections are to be silently disconnected
    #and cleaned up the next time they're checked.
    GOODBYE_PENDING = 3
    #GOODBYE_PENDING connections are to be issued a message
    #(something like "Goodbye! See you soon!"), then kicked.

class Connection:
    """``Connection`` instances represent individual client connections.

    .. class:: Connection(idnum, wlcb, writer)

        This class should only be instantiated by the network
        event loop.

        The constructor arguments are as follows:

        ``reader``
            The :class:`~telnetlib3.TelnetReaer` that reads
            from the underlying socket.

        ``writer``
            The :class:`~telnetlib3.TelnetWriter` that writes
            to the underlying socket.
    """
    def __init__(self,
                 reader: TelnetReader,
                 writer: TelnetWriter,
                 ) -> None:
        self._state = ConnState.NORMAL
        self._postlogin = False
        self._contime = time.monotonic()
        self._acttime = self._contime
        self._inqueue = Queue()
        self._tnw = writer
        self._tnr = reader
        self._descr = writer.get_extra_info('socket').fileno()
        self._loop = asyncio.get_event_loop()

    @property
    def time_connected(self) -> float:
        """The number of seconds this client has been connected."""
        return time.monotonic() - self._contime

    @property
    def descr(self) -> int:
        """The descriptor number of this connection."""
        return self._descr

    @property
    def postlogin(self) -> bool:
        """Whether anyone is logged in through this connection."""
        return self._postlogin
    @postlogin.setter
    def postlogin(self, val: bool) -> None:
        #Is it possible to ensure that this is only called
        #in appropriate places, somehow?
        self._postlogin = val

    @property
    def time_idle(self) -> float:
        """The number of seconds this connection has been silent."""
        return time.monotonic() - self._acttime

    @property
    def state(self) -> ConnState:
        """The connection's state.

        "State" in this context refers to whether or not it
        should be disconnected, and whether the disconnection
        message should be sent to it when that happens.
        """
        return self._state
    @state.setter
    def state(self, val: ConnState) -> None:
        #As with the postlogin setter, this should only be
        #called in a limited number of places.
        self._state = val

    def get_inputline(self, timeout: Optional[float] = None) -> str:
        """Retrieves a line from this connection's input queue.

        The optional *timeout* parameter specifies how many
        seconds this method should block waiting for input
        to become available, if necessary. If *timeout* is
        ``None`` (the default) or a non-positive number, it
        will immediately return or raise :exc:`queue.Empty`.
        """
        if (not timeout) or (timeout < 0) :
            return self._inqueue.get_nowait()
        return self._inqueue.get(timeout)

    def add_inputline(self, line: str) -> None:
        """Adds a line to this connection's input queue."""
        self._acttime = time.monotonic()
        #Queue is unbounded, safe to use nowait:
        self._inqueue.put_nowait(line)

    async def adding_inputlines(self) -> None:
        """Asynchronously adds lines to the input queue as
        they come in."""
        async for line in self._tnr:
            self.add_inputline(line)
            if self._state is not ConnState.NORMAL:
                break

    async def awrite_line(self, line: str) -> None:
        """Asynchronously write a line to this connection.

        This method assumes that the line to write is *not*
        terminated by a newline sequence, and so appends one.
        """
        self._tnw.write(line + NETWORK_NEWLINE)
        await self._tnw.drain()

    def write_line_ts(self, line: str) -> None:
        """Synchronously write a line to this connection
        (thread safe).

        As with :meth:`~.Connection.awrite_line`, this method
        appends a newline sequence.
        """
        future = asyncio.run_coroutine_threadsafe(self.awrite_line(line),
                                                  self._loop)
        #wait for the coroutine to finish:
        future.result()
