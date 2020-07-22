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


class EmptyBlock(object):
    """Represents an empty block"""

    def __init__(self):
        pass

    def __str__(self):
        return " "


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
