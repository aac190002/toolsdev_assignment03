"""
level.py
Asmita Chitale
Assignment 03
ATCM 3311.0U1
07/24/2020
"""


#====================================================== IMPORTS =======================================================#
import blocks
import pymel.core.general as pmcg
import pymel.core.system as pmcs


#====================================================== CONSTS ========================================================#
X = 0  # Element of size tuple
Y = 1  # Element of size tuple
Z = 2  # Element of size tuple
DEFAULT_BLOCK_SIZE = (10, 5, 10)  # Default dimensions for a unit block in Maya
DEFAULT_GROUP_NAME = "groupBlock"  # Default name for the group to look for within the Maya scenes


#====================================================== CLASSES =======================================================#
class MayaSceneLevelGenerator(object):
    """Generates a Maya scene based of a Level model. Part of the Controller"""

    def __init__(self, lvl, block_dimensions=DEFAULT_BLOCK_SIZE, group_name=DEFAULT_GROUP_NAME):
        """
        Sets up the generator
        :param lvl: The level data to create
        :param block_dimensions: The dimensions of a unit block. Must be square (X = Z) but can have any height
        :param group_name: The name of the group containing the shapes comprising the block in each scene file
        """
        self.lvl = lvl
        self.block_dimensions = block_dimensions
        self.group_name = group_name

    def generate(self):
        """
        Generate the maya scene file
        :return: None
        """
        # Pivot for rotation
        pivot = (self.block_dimensions[X]/2.0, 0, self.block_dimensions[Z]/2.0)

        # Go through each level item and place block
        for i in range(self.lvl.size[X]):
            for j in range(self.lvl.size[Y]):
                for k in range(self.lvl.size[Z]):
                    blk = self.lvl.get_block((i, j, k))

                    # Don't worry about Empty or RampDummy blocks
                    if blk.block_type != blocks.BlockType.EMPTY and blk.block_type != blocks.BlockType.RAMP_DUMMY:
                        # Load the scene file
                        pmcs.importFile(pmcs.Path(blk.pth))

                        # Give block a unique name
                        new_name = "{}_{}_{}_{}".format(self.group_name, i, j, k)
                        pmcg.rename(self.group_name, new_name)

                        # Rotate it based on the orientation

                        pmcg.rotate(new_name, [0, 90 * int(blk.orientation), 0], pivot=pivot)

                        # Move it to the correct spot
                        new_spot = [i * self.block_dimensions[X],
                                    j * self.block_dimensions[Y],
                                    k * self.block_dimensions[Z]]
                        pmcg.move(new_name, new_spot)
