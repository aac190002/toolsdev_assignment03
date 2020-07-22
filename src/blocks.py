"""
blocks.py
Asmita Chitale
Assignment 03
ATCM 3311.0U1
07/24/2020
"""


#====================================================== IMPORTS =======================================================#
from enum import Enum
from pymel.core.system import Path


#====================================================== CONSTS ========================================================#
DEFAULT_WEIGHT = 1.0


#====================================================== CLASSES =======================================================#
class BlockType(Enum):
    """Enums for all valid block types"""
    EMPTY = 0
    START = 1
    END = 2
    DEAD_END = 3
    STRAIGHT = 4
    RAMP = 5
    T_INTERSECTION = 6
    CROSS = 7
    CURVED = 8
    
    
class Orientation(Enum):
    """Orientation of blocks, in 90 degree CCW increments. Says where the base of the block is"""
    NORTH = 0
    WEST = 1
    SOUTH = 2
    EAST = 3


class EmptyBlock(object):
    """Represents an empty block. Can have any orientation"""

    def __init__(self, orientation=Orientation.NORTH):
        self.block_type = BlockType.EMPTY
        self.orientation = orientation

    def __str__(self):
        return " "


class StartBlock(object):
    """Represents a start block. Can have any orientation

    Defined with exit to the south

    +-----+
    |  S  |
    +-+ +-+
      | |
    """

    def __init__(self, orientation=Orientation.NORTH):
        self.block_type = BlockType.START
        self.orientation = orientation

    def __str__(self):
        return "S"


class EndBlock(object):
    """Represents an end block. Can have any orientation

    Defined with entrance to the north

      | |
    +-+ +-+
    |  E  |
    +-----+
    """

    def __init__(self, orientation=Orientation.NORTH):
        self.block_type = BlockType.END
        self.orientation = orientation

    def __str__(self):
        return "E"


class DeadEndBlock(object):
    """Represents a dead end block. Can have any orientation

    Defined with entrance to the north

      | |
    +-+ +-+
    |  X  |
    +-----+
    """

    def __init__(self, orientation=Orientation.NORTH):
        self.block_type = BlockType.DEAD_END
        self.orientation = orientation

    def __str__(self):
        return "X"


class StraightBlock(object):
    """Represents a straight block. Can have any orientation

    Defined with entrance to the north. Is symmetric

      | |
      | |
      | |
    """

    def __init__(self, orientation=Orientation.NORTH):
        self.block_type = BlockType.STRAIGHT
        self.orientation = orientation

    def __str__(self):
        return "|" # Doesn't show orientation


class RampBlock(object):
    """Represents a ramp block. Can have any orientation

    Defined with entrance to the north (is at a higher level at the south)

      | |
      |V|
      | |
    """

    def __init__(self, orientation=Orientation.NORTH):
        self.block_type = BlockType.RAMP
        self.orientation = orientation

    def __str__(self):
        return "R"  # Doesn't show orientation


class TIntersectionBlock(object):
    """Represents a T intersection block. Can have any orientation

    Defined with entrance to the north. Can be entered from any side

         | |
    -----+ +-----

    -------------
    """

    def __init__(self, orientation=Orientation.NORTH):
        self.block_type = BlockType.T_INTERSECTION
        self.orientation = orientation

    def __str__(self):
        return u"T"  # Doesn't show orientation :(


class CrossBlock(object):
    """Represents a cross block. Can have any orientation

    Defined with entrance to the north. Can be entered from any side

         | |
    -----+ +-----

    -----+ +-----
         | |
    """

    def __init__(self, orientation=Orientation.NORTH):
        self.block_type = BlockType.CROSS
        self.orientation = orientation

    def __str__(self):
        return "+"


class CurvedBlock(object):
    """Represents a curved block. Can have any orientation

    Defined with entrance to the north. Can be entered from any side

    | |
    | +-----
    |
    +-------
    """

    def __init__(self, orientation=Orientation.NORTH):
        self.block_type = BlockType.CURVED
        self.orientation = orientation

    def __str__(self):
        return "L"  # Doesn't show orientation


class BlockFile(object):
    """Location and type of a Block File. Part of the Controller"""

    def __init__(self, pth, block_type, weight=DEFAULT_WEIGHT):
        """
        Create the Block File
        :param pth: Path to the scene file for the block. The block should be drawn as shown in its corresponding
            class
        :param block_type: Which type of block this scene file represents. Must be a BlockType
        :param weight: The randomization weight, optional
        """
        self.pth = Path(pth)
        self.block_type = block_type
        self.weight = weight
