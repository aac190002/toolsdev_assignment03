"""
blocks.py
Asmita Chitale
Assignment 03
ATCM 3311.0U1
07/24/2020
"""


#====================================================== IMPORTS =======================================================#
from enum import Enum


#====================================================== CONSTS ========================================================#
DEFAULT_WEIGHT = 1.0
X = 0  # Element of size tuple
Y = 1  # Element of size tuple
Z = 2  # Element of size tuple


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
    RAMP_DUMMY = 9


# This is a const but closely linked and related to BlockType
BLOCK_TYPE_STR = {  # Get block type as a string for the user
    BlockType.EMPTY: "Empty",
    BlockType.START: "Start",
    BlockType.END: "End",
    BlockType.DEAD_END: "Dead End",
    BlockType.STRAIGHT: "Straight",
    BlockType.RAMP: "Ramp",
    BlockType.T_INTERSECTION: "T-Intersection",
    BlockType.CROSS: "Cross",
    BlockType.CURVED: "Curved",
    BlockType.RAMP_DUMMY: "Ramp Dummy",
}
    
    
class Orientation(Enum):
    """Orientation of blocks, in 90 degree CCW increments. Says where the base of the block is"""
    NORTH = 0
    WEST = 1
    SOUTH = 2
    EAST = 3


class EmptyBlock(object):
    """Represents an empty block. Can have any orientation. Part of the Model"""

    def __init__(self, pth=None, weight=DEFAULT_WEIGHT, orientation=Orientation.NORTH):
        self.block_type = BlockType.EMPTY
        self.pth = pth  # Unused
        self.weight = weight  # Unused
        self.orientation = orientation  # Unused
        self.length = -1  # Unused

    def __str__(self):
        return " "

    def adjacent(self, pos):
        """
        Returns all adjacent positions given the block's position
        :param pos: The block's position
        :return: List of adjacent positions
        """
        return []


class StartBlock(object):
    """Represents a start block. Can have any orientation. Part of the Model

    Defined with exit to the south

    +-----+
    |  S  |
    +-+ +-+
      | |
    """

    def __init__(self, pth=None, weight=DEFAULT_WEIGHT, orientation=Orientation.NORTH):
        self.block_type = BlockType.START
        self.pth = pth
        self.weight = weight
        self.orientation = orientation
        self.length = -1

    def __str__(self):
        return "S"

    def adjacent(self, pos):
        """
        Returns all adjacent positions given the block's position
        :param pos: The block's position
        :return: List of adjacent positions
        """
        if self.orientation == Orientation.NORTH:
            return [(pos[X], pos[Y], pos[Z] + 1)]
        elif self.orientation == Orientation.WEST:
            return [(pos[X] + 1, pos[Y], pos[Z])]
        elif self.orientation == Orientation.SOUTH:
            return [(pos[X], pos[Y], pos[Z] - 1)]
        else:
            return [(pos[X] - 1, pos[Y], pos[Z])]


class EndBlock(object):
    """Represents an end block. Can have any orientation. Part of the Model

    Defined with entrance to the north

      | |
    +-+ +-+
    |  E  |
    +-----+
    """

    def __init__(self, pth=None, weight=DEFAULT_WEIGHT, orientation=Orientation.NORTH):
        self.block_type = BlockType.END
        self.pth = pth
        self.weight = weight
        self.orientation = orientation
        self.length = -1

    def __str__(self):
        return "E"

    def adjacent(self, pos):
        """
        Returns all adjacent positions given the block's position
        :param pos: The block's position
        :return: List of adjacent positions
        """
        if self.orientation == Orientation.NORTH:
            return [(pos[X], pos[Y], pos[Z] - 1)]
        elif self.orientation == Orientation.WEST:
            return [(pos[X] - 1, pos[Y], pos[Z])]
        elif self.orientation == Orientation.SOUTH:
            return [(pos[X], pos[Y], pos[Z] + 1)]
        else:
            return [(pos[X] + 1, pos[Y], pos[Z])]


class DeadEndBlock(object):
    """Represents a dead end block. Can have any orientation. Part of the Model

    Defined with entrance to the north

      | |
    +-+ +-+
    |  X  |
    +-----+
    """

    def __init__(self, pth=None, weight=DEFAULT_WEIGHT, orientation=Orientation.NORTH):
        self.block_type = BlockType.DEAD_END
        self.pth = pth
        self.weight = weight
        self.orientation = orientation
        self.length = -1

    def __str__(self):
        return "X"

    def adjacent(self, pos):
        """
        Returns all adjacent positions given the block's position
        :param pos: The block's position
        :return: List of adjacent positions
        """
        if self.orientation == Orientation.NORTH:
            return [(pos[X], pos[Y], pos[Z] - 1)]
        elif self.orientation == Orientation.WEST:
            return [(pos[X] - 1, pos[Y], pos[Z])]
        elif self.orientation == Orientation.SOUTH:
            return [(pos[X], pos[Y], pos[Z] + 1)]
        else:
            return [(pos[X] + 1, pos[Y], pos[Z])]


class StraightBlock(object):
    """Represents a straight block. Can have any orientation. Part of the Model

    Defined with entrance to the north. Is symmetric

      | |
      | |
      | |
    """

    def __init__(self, pth=None, weight=DEFAULT_WEIGHT, orientation=Orientation.NORTH):
        self.block_type = BlockType.STRAIGHT
        self.pth = pth
        self.weight = weight
        self.orientation = orientation
        self.length = -1

    def __str__(self):
        if self.orientation == Orientation.NORTH or self.orientation == Orientation.SOUTH:
            return "|"
        else:
            return "-"

    def adjacent(self, pos):
        """
        Returns all adjacent positions given the block's position
        :param pos: The block's position
        :return: List of adjacent positions
        """
        if self.orientation == Orientation.NORTH or self.orientation == Orientation.SOUTH:
            return [(pos[X], pos[Y], pos[Z] - 1), (pos[X], pos[Y], pos[Z] + 1)]
        else:
            return [(pos[X] - 1, pos[Y], pos[Z]), (pos[X] + 1, pos[Y], pos[Z])]


class RampBlock(object):
    """Represents a ramp block. Can have any orientation. Part of the Model

    Defined with entrance to the north (is at a higher level at the south)

      | |
      |V|
      | |
    """

    def __init__(self, pth=None, weight=DEFAULT_WEIGHT, orientation=Orientation.NORTH):
        self.block_type = BlockType.RAMP
        self.pth = pth
        self.weight = weight
        self.orientation = orientation
        self.length = -1

    def __str__(self):
        if self.orientation == Orientation.NORTH:
            return "V"
        elif self.orientation == Orientation.WEST:
            return ">"
        elif self.orientation == Orientation.SOUTH:
            return "^"
        else:
            return "<"

    def adjacent(self, pos):
        """
        Returns all adjacent positions given the block's position
        :param pos: The block's position
        :return: List of adjacent positions
        """
        if self.orientation == Orientation.NORTH:
            return [(pos[X], pos[Y], pos[Z] - 1), (pos[X], pos[Y] + 1, pos[Z] + 1)]
        elif self.orientation == Orientation.WEST:
            return [(pos[X] - 1, pos[Y], pos[Z]), (pos[X] + 1, pos[Y] + 1, pos[Z])]
        elif self.orientation == Orientation.SOUTH:
            return [(pos[X], pos[Y], pos[Z] + 1), (pos[X], pos[Y] + 1, pos[Z] - 1)]
        else:
            return [(pos[X] + 1, pos[Y], pos[Z]), (pos[X] - 1, pos[Y] + 1, pos[Z])]


class RampDummy(object):
    """Represents the space above a ramp block. Can have any orientation. Part of the Model

    Defined with entrance to the north (is at a higher level at the south)

      | |
      |V|
      | |
    """

    def __init__(self, pth=None, weight=DEFAULT_WEIGHT, orientation=Orientation.NORTH):
        self.block_type = BlockType.RAMP_DUMMY
        self.pth = pth  # Unused
        self.weight = weight  # Unused
        self.orientation = orientation
        self.length = -1  # Unused

    def __str__(self):
        return "R"  # Doesn't show orientation :(

    def adjacent(self, pos):
        """
        Returns all adjacent positions given the block's position
        :param pos: The block's position
        :return: List of adjacent positions
        """
        if self.orientation == Orientation.NORTH:
            return [(pos[X], pos[Y], pos[Z] + 1)]
        elif self.orientation == Orientation.WEST:
            return [(pos[X] + 1, pos[Y], pos[Z])]
        elif self.orientation == Orientation.SOUTH:
            return [(pos[X], pos[Y], pos[Z] - 1)]
        else:
            return [(pos[X] - 1, pos[Y], pos[Z])]


class TIntersectionBlock(object):
    """Represents a T intersection block. Can have any orientation. Part of the Model

    Defined with entrance to the north. Can be entered from any side

         | |
    -----+ +-----

    -------------
    """

    def __init__(self, pth=None, weight=DEFAULT_WEIGHT, orientation=Orientation.NORTH):
        self.block_type = BlockType.T_INTERSECTION
        self.pth = pth
        self.weight = weight
        self.orientation = orientation
        self.length = -1

    def __str__(self):
        return "T"  # Doesn't show orientation :(

    def adjacent(self, pos):
        """
        Returns all adjacent positions given the block's position
        :param pos: The block's position
        :return: List of adjacent positions
        """
        if self.orientation == Orientation.NORTH:
            return [(pos[X], pos[Y], pos[Z] - 1), (pos[X] - 1, pos[Y], pos[Z]), (pos[X] + 1, pos[Y], pos[Z])]
        elif self.orientation == Orientation.WEST:
            return [(pos[X] - 1, pos[Y], pos[Z]), (pos[X], pos[Y], pos[Z] - 1), (pos[X], pos[Y], pos[Z] + 1)]
        elif self.orientation == Orientation.SOUTH:
            return [(pos[X], pos[Y], pos[Z] + 1), (pos[X] - 1, pos[Y], pos[Z]), (pos[X] + 1, pos[Y], pos[Z])]
        else:
            return [(pos[X] + 1, pos[Y], pos[Z]), (pos[X], pos[Y], pos[Z] - 1), (pos[X], pos[Y], pos[Z] + 1)]


class CrossBlock(object):
    """Represents a cross block. Can have any orientation. Part of the Model

    Defined with entrance to the north. Can be entered from any side

         | |
    -----+ +-----

    -----+ +-----
         | |
    """

    def __init__(self, pth=None, weight=DEFAULT_WEIGHT, orientation=Orientation.NORTH):
        self.block_type = BlockType.CROSS
        self.pth = pth
        self.weight = weight
        self.orientation = orientation
        self.length = -1

    def __str__(self):
        return "+"

    def adjacent(self, pos):
        """
        Returns all adjacent positions given the block's position
        :param pos: The block's position
        :return: List of adjacent positions
        """
        return [(pos[X], pos[Y], pos[Z] - 1), (pos[X], pos[Y], pos[Z] + 1),
                (pos[X] - 1, pos[Y], pos[Z]), (pos[X] + 1, pos[Y], pos[Z])]


class CurvedBlock(object):
    """Represents a curved block. Can have any orientation. Part of the Model

    Defined with entrance to the north. Can be entered from any side

    | |
    | +-----
    |
    +-------
    """

    def __init__(self, pth=None, weight=DEFAULT_WEIGHT, orientation=Orientation.NORTH):
        self.block_type = BlockType.CURVED
        self.pth = pth
        self.weight = weight
        self.orientation = orientation
        self.length = -1

    def __str__(self):
        return "C"  # Doesn't show orientation :(

    def adjacent(self, pos):
        """
        Returns all adjacent positions given the block's position
        :param pos: The block's position
        :return: List of adjacent positions
        """
        if self.orientation == Orientation.NORTH:
            return [(pos[X], pos[Y], pos[Z] - 1), (pos[X] + 1, pos[Y], pos[Z])]
        elif self.orientation == Orientation.WEST:
            return [(pos[X] - 1, pos[Y], pos[Z]), (pos[X], pos[Y], pos[Z] - 1)]
        elif self.orientation == Orientation.SOUTH:
            return [(pos[X], pos[Y], pos[Z] + 1), (pos[X] - 1, pos[Y], pos[Z])]
        else:
            return [(pos[X] + 1, pos[Y], pos[Z]), (pos[X], pos[Y], pos[Z] + 1)]


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
        self.pth = pth
        self.block_type = block_type
        self.weight = weight

    def make_block(self, orientation=Orientation.NORTH):
        """
        Makes a block from the block file. Note that a base class is unnecessary due to duck typing
        :return: The block
        """
        if not self.pth:
            return EmptyBlock()
        if self.block_type == BlockType.START:
            return StartBlock(pth=self.pth, weight=self.weight, orientation=orientation)
        if self.block_type == BlockType.END:
            return EndBlock(pth=self.pth, weight=self.weight, orientation=orientation)
        if self.block_type == BlockType.DEAD_END:
            return DeadEndBlock(pth=self.pth, weight=self.weight, orientation=orientation)
        if self.block_type == BlockType.STRAIGHT:
            return StraightBlock(pth=self.pth, weight=self.weight, orientation=orientation)
        if self.block_type == BlockType.RAMP:
            return RampBlock(pth=self.pth, weight=self.weight, orientation=orientation)
        if self.block_type == BlockType.T_INTERSECTION:
            return TIntersectionBlock(pth=self.pth, weight=self.weight, orientation=orientation)
        if self.block_type == BlockType.CROSS:
            return CrossBlock(pth=self.pth, weight=self.weight, orientation=orientation)
        if self.block_type == BlockType.CURVED:
            return CurvedBlock(pth=self.pth, weight=self.weight, orientation=orientation)
        else:
            return EmptyBlock()
