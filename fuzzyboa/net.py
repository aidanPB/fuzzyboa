"""net -- Low-level network routines"""
#stdlib imports:
import asyncio
import collections.abc as collabc
from concurrent.futures import Future
import itertools
from typing import Callable
#third-party imports:
from telnetlib3 import TelnetReader, TelnetWriter

def gen_wlcb(loop: asyncio.AbstractEventLoop,
              writer: TelnetWriter
              ) -> Callable[[str], Future] :
    """Creates a callback that writes a string to *writer*
    in a threadsafe manner.
    """
    def cb(line: str):
        loop.call_soon_threadsafe(writer.write, line)
        f = asyncio.run_coroutine_threadsafe(writer.drain(),
                                             loop)
        return f
    return cb

class IntAwaitPool(collabc.Generator):
    """A pool yielding (awaitables that yield) integers."""
    def __init__(self, con=None):
        self._count = itertools.count()
        self._top = next(self._count)
        self._rvs = set()
        self._con = asyncio.Condition() if con is None else con
        self._stopped = False

    def send(self, value):
        if self._stopped: raise StopIteration
        if value is None:
            async def awaitable():
                async with self._con:
                    if self._stopped: raise StopIteration
                    if len(self._rvs) == 0:
                        yv = self._top
                        self._top = next(self._count)
                    else:
                        yv = self._rvs.pop()
                    return yv
            return awaitable()
        elif 0 <= value < self._top:
            self._rvs.add(value)

    def throw(self, typ, val=None, tb=None):
        try:
            return super().throw(typ, val, tb)
        except (Exception, GeneratorExit) as exc:
            self._stopped = True
            raise StopIteration from exc
