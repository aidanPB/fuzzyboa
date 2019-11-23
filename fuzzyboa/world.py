"""
``world``: Objects that make up the game world
==============================================

.. module:: fuzzyboa.world
.. moduleauthor:: Aidan Pitt-Brooke <f.sylvestris@gmail.com>
"""
#stdlib imports:
from enum import Enum, Flag
from typing import Optional, Union
#sibling imports:
from . import clientconn as cconn

__all__ = ('ObjKind',
           'Permission',
           'WObject',
           )

class ObjKind(Enum):
    """The kinds of world objects."""
    THING = ''
    PLAYER = 'P'
    ROOM = 'R'
    PROGRAM = 'F'
    EXIT = 'E'
    ACTION = 'E'
    GARBAGE = 'G'
    NOTYPE = '!'

class Permission(Flag):
    """Flags describing what can be done to/by an object."""
    WIZARD = 0x10
    LINK_OK = 0x20
    DARK = 0x40
    DEBUG = 0x40
    #INTERNAL = 0x80
    STICKY = 0x100
    SETUID = 0x100
    BUILDER = 0x200
    CHOWN_OK = 0x400
    JUMP_OK = 0x800
    #0x1000 unassigned
    #0x2000 unassigned
    KILL_OK = 0x4000
    GUEST = 0x8000
    HAVEN = 0x10000
    HARDUID = 0x10000
    ABODE = 0x20000
    AUTOSTART = 0x20000
    MUCKER = 0x40000
    QUELL = 0x80000
    SMUCKER = 0x100000
    #INTERACTIVE = 0x200000
    #OBJECT_CHANGED = 0x400000
    #0x800000 unassigned
    VEHICLE = 0x1000000
    ZOMBIE = 0x2000000
    #LISTENER = 0x4000000
    XFORCIBLE = 0x8000000
    #READMODE = 0x10000000
    #SANEBIT = 0x20000000
    YIELD = 0x40000000
    OVERT = 0x80000000

DBRef = Union[int, 'WObject']
PlayerRef = Union[int, 'WPlayer']

class WObject:
    '''An object that forms part of the game world.'''
    def __init__(self,
                 dbref: int,
                 typeflag: ObjectKind,
                 flags: Permission,
                 name: str,
                 owner: PlayerRef,
                 loc: DBRef,
                 ):
        self._dbref = dbref
        self._type = typeflag
        self._flags = flags
        self._name = name
        self._owner = owner
        self._loc = loc
