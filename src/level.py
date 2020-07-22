"""
level.py
Asmita Chitale
Assignment 03
ATCM 3311.0U1
07/24/2020
"""


#====================================================== IMPORTS =======================================================#
import blocks


#====================================================== CONSTS ========================================================#
X = 0  # Element of size tuple
Y = 1  # Element of size tuple
Z = 2  # Element of size tuple
MINIMUM_SIZE = (1,1,2)  # Need room for at least a start block and an end block


#====================================================== CLASSES =======================================================#
class Level(object):
    """Represents an instance level full of block instances"""

    def __init__(self, size=(1,1,2)):
        """
        Generates an empty level. The blocks are to be filled in by the generator.
        :param size: The X, Y, and Z size of the level.
        """
        self.size = size
        self._lvl = [[[blocks.EmptyBlock() for k in range(size[Z])] for j in range(size[Y])] for i in range(size[X])]

    def is_valid(self, pos):
        """
        Returns whether the position is valid
        :param pos: The (X,Y,Z) position
        :return: True if valid else False
        """
        ret = True
        for coord in [X,Y,Z]:
            if pos[coord] < 0 or pos[coord] >= self.size[coord]:
                ret = False
        return ret

    def is_empty(self, pos):
        """
        Returns whether the block at pos is empty
        :param pos: The (X,Y,Z) position
        :return: If valid, True if empty else False. None if invalid.
        """
        if not self.is_valid(pos):
            return None
        if self._lvl[pos[X]][pos[Y]][pos[Z]].block_type == blocks.BlockType.EMPTY:
            return True

    def __str__(self):
        """
        Print representation of this level in layers
        :return: String representation of this level
        """
        tmp = []
        for layer in reversed(range(self.size[Y])):
            # Print each layer
            tmp.append("Layer {}:".format(layer))
            tmp.append("."*(self.size[X] + 2))  # Level border

            for row in range(self.size[Z]):
                # Print each row
                rowtxt = "."

                for cell in range(self.size[X]):
                    rowtxt += str(self._lvl[cell][layer][row])

                rowtxt += "."
                tmp.append(rowtxt)

            tmp.append("."*(self.size[X] + 2))  # Level border
            tmp.append("")
            
        return "\n".join(tmp)
