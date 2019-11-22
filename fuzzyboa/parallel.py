"""
:mod:`parallel` -- Parallelism support
======================================

.. module:: fuzzyboa.parallel
    :synopsis: Parallelism support for fuzzyboa.
.. moduleauthor:: Aidan Pitt-Brooke <f.sylvestris@gmail.com>
"""
#stdlib imports:
import asyncio
from collections.abc import Callable
import concurrent.futures as confutures
from enum import Enum, unique
from typing import Optional, Union

@unique
class Mode(Enum):
    """Modes of parallelism."""
    NONE = 1
    #Disable parallelism altogether. Run everything in the
    #network event loop.
    THREAD = 2
    #Use OS threads for parallelism.
    PROCESS = 3
    #Use subprocesses for parallelism.
    MIXED = 4
    #Use threads for file operations and processes for
    #CPU-bound operations.

_lle = threading.local()
#If we have multiple event loops for some reason, each will
#run in a single, separate thread. A threading.local object
#is thus suitable for "loop-local" values.

def _instantiate_executor(mode: Mode,
                          cpuop: bool = False,
                          max_workers: Optional[int] = None
                          ) -> Optional[confutures.Executor] :
    """Create an :class:`~concurrent.futures.Executor` instance
    appropriate to the given *mode*."""
    if mode is Mode.NONE:
        return None
    if mode is Mode.THREAD or (mode is Mode.MIXED and not cpuop):
        return confutures.ThreadPoolExecutor(max_workers)
    if mode is Mode.PROCESS or (mode is Mode.MIXED and cpuop):
        return confutures.ProcessPoolExecutor(max_workers)
    #Only way to reach here is if mode isn't a Mode:
    raise TypeError("Inappropriate type for mode argument.")

async def _ensure_executor(mode: Mode,
                           cpuop: bool = False,
                           max_workers: Optional[int] = None
                           ) -> Optional[confutures.Executor] :
    """Ensure that the current event loop has an ``Executor``
    appropriate to the given *mode*, and return it."""
    if mode is Mode.NONE:
        return None
    if mode is not Mode.MIXED:
        try:
            return _lle.pool
        except AttributeError:
            _lle.pool = _instantiate_executor(mode, cpuop, max_workers)
            return _lle.pool
    if mode is Mode.MIXED:
        if cpuop:
            try:
                return _lle.ppool
            except AttributeError:
                _lle.ppool = confutures.ProcessPoolExecutor(max_workers)
                return _lle.ppool
        else:
            try:
                return _lle.tpool
            except AttributeError:
                _lle.tpool = confutures.ThreadPoolExecutor(max_workers)
                return _lle.tpool

async def run_in_executor(func: Callable,
                          mode: Mode,
                          *args,
                          cpuop: bool = False,
                          max_workers: Optional[int] = None
                          ) -> Union[asyncio.Future, asyncio.Handle]:
    """Arrange for *func* to be called in an executor.

    The keyword-only argument *cpuop* is only checked in
    ``MIXED`` mode. If it's ``True``, *func* is to be
    considered CPU-bound. Otherwise, *func* is assumed to be
    resource-bound, like a file operation.

    If *mode* is ``NONE``, *func* is scheduled to run in the
    event loop using ``call_soon()``, and this coroutine
    returns the :class:`asyncio.Handle` thus created.
    Otherwise, *func* is scheduled to run in an appropriate
    :class:`~concurrent.futures.Executor` using the current
    event loop's ``run_in_executor`` method, and the
    :class:`asyncio.Future` that method creates is returned.

    The keyword-only argument *max_workers* is used to
    construct the ``Executor``, if necessary.
    """
    loop = asyncio.get_event_loop()
    if mode is Mode.NONE:
        return loop.call_soon(func, *args)
    e6r = await _ensure_executor(mode, cpuop, max_workers)
    return loop.run_in_executor(e6r, func, *args)
