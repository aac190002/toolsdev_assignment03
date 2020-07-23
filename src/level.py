"""
level.py
Asmita Chitale
Assignment 03
ATCM 3311.0U1
07/24/2020
"""


#====================================================== IMPORTS =======================================================#
import blocks
import random


#====================================================== CONSTS ========================================================#
X = 0  # Element of size tuple
Y = 1  # Element of size tuple
Z = 2  # Element of size tuple
MINIMUM_SIZE = (1, 1, 2)  # Need room for at least a start block and an end block


#====================================================== CLASSES =======================================================#
class Level(object):
    """Represents an instance level full of block instances. This is the Model"""

    def __init__(self, size=MINIMUM_SIZE):
        """
        Generates an empty level. The blocks are to be filled in by the generator
        :param size: The X, Y, and Z size of the level in blocks
        """
        self.size = size
        self._lvl = [[[blocks.EmptyBlock() for k in range(size[Z])] for j in range(size[Y])] for i in range(size[X])]
        self.length = 0

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
        :return: If valid, True if empty else False. None if invalid
        """
        if not self.is_valid(pos):
            return None
        if self._lvl[pos[X]][pos[Y]][pos[Z]].block_type == blocks.BlockType.EMPTY:
            return True

    def place_block(self, block, pos):
        """
        Place a block in the level
        :param block: The block object to place
        :param pos: The position (X,Y,Z) in which to place it
        :return: True if place was successful else False
        """
        if self.is_valid(pos):
            self._lvl[pos[X]][pos[Y]][pos[Z]] = block
            return True
        else:
            return False

    def get_block(self, pos):
        """
        Returns the block at a position
        :param pos: The position (X,Y,Z) of the block
        :return: The block
        """
        return self._lvl[pos[X]][pos[Y]][pos[Z]]

    def find_longest_dead_end(self):
        """
        Returns the position of the longest dead end or None if there are no dead ends
        :return: The (X,Y,Z) position of the longest dead end
        """
        max_len = -1
        max_pos = None
        for i in range(self.size[X]):
            for j in range(self.size[Y]):
                for k in range(self.size[Z]):
                    blk = self.get_block((i, j, k))
                    if blk.block_type == blocks.BlockType.DEAD_END:
                        if blk.length > max_len:
                            max_pos = (i, j, k)
                            max_len = blk.length
        return max_pos

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


class CannotGenerateLevelError(Exception):
    """Represents an error when the level could not be generated for some reason"""
    pass


class LevelGenerator(object):
    """Generates a level based on settings given. This is the Controller"""

    def __init__(self, block_list, size=MINIMUM_SIZE, minimum_length=None, maximum_length=None, seed=None):
        """
        Creates a generator with the given settings. Settings can be changed later
        :param block_list: List of BlockFiles allowed in level generation. At least one start and end block must be
            present
        :param size: The (X,Y,Z) size of the level in blocks
        :param minimum_length: The minimum length from start to finish. None means no minimum length. This is just a
            suggestion - if forced, the program may have to end the level early
        :param maximum_length: The maximum length from start to finish. None means no maximum length
        :param seed: The seed for the random number generator. None means use a random seed
        """
        self.block_list = block_list
        self.size = size
        self.minimum_length = minimum_length
        self.maximum_length = maximum_length
        self.seed = seed

    def check_size(self):
        """
        Returns whether the size is valid
        :return: True if valid size else False
        """
        for coord in [X, Y, Z]:
            if self.size[coord] < MINIMUM_SIZE[coord]:
                return False
        return True

    def _check_all_pos(self, current_pos, lvl):
        """
        Filter that makes sure all adjacent blocks are valid
        :param current_pos: The block's position
        :param lvl: The level
        :return: The filter
        """
        def inner_filter(block):
            for pos in block.adjacent(current_pos):
                if not lvl.is_valid(pos):
                    return False
            return True
        return inner_filter

    def _get_connected_block_list(self, block, current_pos, lvl):
        """
        Returns a list of the blocks connected to the current block
        :param block: The block to check
        :param current_pos: The block's position
        :param lvl: The level
        :return: The list of connected blocks
        """
        spots = block.adjacent(current_pos)
        spots = filter(lvl.is_valid, spots)
        blist = [][:]
        for spot in spots:
            if not lvl.is_empty(spot):
                blk = lvl.get_block(spot)
                if current_pos in blk.adjacent(spot):
                    # That block is adjacent to this and visa versa, therefore mutually adjacent
                    blist.append(blk)
        return blist

    def _check_min_length(self, current_pos, lvl, other_spots):
        """
        Filter that checks the minimum length based on the adjacent blocks
        :param current_pos: The block's position
        :param lvl: The level
        :param other_spots: Whether there are other spots. If so, dead ends are OK
        :return: The filter
        """
        def inner_filter(block):
            if block.block_type != blocks.BlockType.END and block.block_type != blocks.BlockType.DEAD_END:
                return True  # Don't filter non-end blocks based off of minimum length
            if other_spots and block.block_type == blocks.BlockType.DEAD_END:
                return True  # Don't filter dead end blocks if there are other chances for an end
            blist = self._get_connected_block_list(block, current_pos, lvl)
            prev_len = min(blist, key=(lambda blk: blk.length))
            return self.minimum_length <= prev_len.length + 1  # Keep end blocks if minimum length reached
        return inner_filter

    def _check_max_length(self, current_pos, lvl):
        """
        Filter that checks the minimum length based on the adjacent blocks
        :param current_pos: The block's position
        :param lvl: The level
        :return: The filter
        """
        def inner_filter(block):
            if block.block_type == blocks.BlockType.END or block.block_type == blocks.BlockType.DEAD_END:
                return True  # Don't filter end blocks based off of maximum length
            blist = self._get_connected_block_list(block, current_pos, lvl)
            prev_len = min(blist, key=(lambda blk: blk.length))
            return self.maximum_length > prev_len.length + 1  # Keep non-end blocks if max length not reached
        return inner_filter

    def _check_mutual_adjacent(self, current_pos, lvl):
        """
        Filter that makes sure that the block is mutually adjacent to any adjacent blocks. One spot must not be empty
        :param current_pos: The block's position
        :param lvl: The level
        :return: The filter
        """
        def inner_filter(block):
            spots = block.adjacent(current_pos)
            spots = filter(lvl.is_valid, spots)
            one_not_empty = False
            for spot in spots:
                if not lvl.is_empty(spot):
                    one_not_empty = True
                    blk = lvl.get_block(spot)
                    if current_pos not in blk.adjacent(spot):
                        # Mismatch, block exists but not mutually adjacent
                        return False
            if not one_not_empty:
                return False
            # Need to search for any blocks to which this block was supposed to be adjacent
            possible_spots = [][:]
            for j in [current_pos[Y], current_pos[Y]-1]:  # Y-1 needed for ramps
                possible_spots.extend([(current_pos[X] + 1, j, current_pos[Z] + 0),
                                       (current_pos[X] - 1, j, current_pos[Z] + 0),
                                       (current_pos[X] + 0, j, current_pos[Z] + 1),
                                       (current_pos[X] + 0, j, current_pos[Z] - 1)])
            for spot in possible_spots:
                if lvl.is_valid(spot) and not lvl.is_empty(spot):
                    blk = lvl.get_block(spot)
                    if current_pos in blk.adjacent(spot):
                        # If this block is adjacent to that, that must be adjacent to this unless ramp
                        if blk.block_type != blocks.BlockType.RAMP and spot not in block.adjacent(current_pos):
                            return False
            return True
        return inner_filter


    def _check_ramps(self, current_pos, lvl, other_spots):
        """
        Filter that makes sure ramps will work
        :param current_pos: The ramp's position
        :param lvl: The level
        :param other_spots: The other pending spots
        :return: The filter
        """
        def inner_filter(block):
            if block.block_type != blocks.BlockType.RAMP:
                return True  # This filter only affects ramps
            # Make sure dummy spot is empty
            dummy_spot = (current_pos[X], current_pos[Y] + 1, current_pos[Z])
            if not lvl.is_empty(dummy_spot):
                return False  # Remove this ramp
            # Make sure the dummy spot is not supposed to hold some block
            if dummy_spot in other_spots:
                return False  # Remove this ramp
            # Make tmp dummy and make sure its adjacent spot is empty
            tmp_dummy = blocks.RampDummy(orientation=block.orientation)
            for spot in tmp_dummy.adjacent(dummy_spot):
                if not lvl.is_empty(spot):
                    return False  # Remove this ramp
            return True  # Accept this ramp
        return inner_filter


    def _all_orientations(self, blockf):
        """
        Returns blocks of all orientations from a BlockFile
        :param blockf: The BlockFile
        :return: A list of blocks of all orientations
        """
        return [blockf.make_block(orientation=blocks.Orientation.NORTH),
                blockf.make_block(orientation=blocks.Orientation.WEST),
                blockf.make_block(orientation=blocks.Orientation.SOUTH),
                blockf.make_block(orientation=blocks.Orientation.EAST)]

    def _get_valid_blocks(self, current_spot, lvl, placed_start, placed_end, start_blocks, end_blocks, dead_end_blocks,
                          other_blocks, other_spots, force_end=False):
        """
        Returns a list of valid blocks to go at a spot. Block must not lead off the edge of the world and must be
        mutually adjacent to a block, unless it is the starting block
        :param current_spot: The spot to check for valid blocks
        :param lvl: The level so far
        :param placed_start: Whether the start block has been placed
        :param placed_end: Whether the end block has been placed
        :param start_blocks: The list of start blocks
        :param end_blocks: The list of end blocks
        :param dead_end_blocks: The list of dead end blocks
        :param other_blocks: The list of other blocks
        :param other_spots: List of other spots besides this one
        :param force_end: Whether to force placement of the end block. Should only be used for recursion
        :return: A list of valid blocks at this spot
        """
        # List to return
        ret = [][:]

        # If start hasn't been placed, only suggest start blocks
        if not placed_start:
            for blockf in start_blocks:
                ret.extend(self._all_orientations(blockf))
            # Make sure all adjacent blocks are valid
            ret = filter(self._check_all_pos(current_spot, lvl), ret)
            return ret
        else:
            # Generate every possible block at this position
            if force_end or not placed_end:
                for blockf in end_blocks:
                    ret.extend(self._all_orientations(blockf))
            if not force_end:
                for blockf in dead_end_blocks:
                    ret.extend(self._all_orientations(blockf))
                for blockf in other_blocks:
                    ret.extend(self._all_orientations(blockf))

            # Make sure all adjacent blocks are valid
            ret = filter(self._check_all_pos(current_spot, lvl), ret)

            # Make sure all blocks are mutually adjacent to any adjacent blocks
            ret = filter(self._check_mutual_adjacent(current_spot, lvl), ret)

            # Only allow end blocks if the minimum length has been reached. Dead ends are OK if there are other spots
            if not force_end and self.minimum_length:
                ret = filter(self._check_min_length(current_spot, lvl, len(other_spots) > 0), ret)

            # Only allow non-end blocks if the maximum length hasn't been reached
            if not force_end and self.maximum_length:
                ret = filter(self._check_max_length(current_spot, lvl), ret)

            # Filter the valid ramps
            ret = filter(self._check_ramps(current_spot, lvl, other_spots), ret)

            # If there are no valid blocks, end the level
            if len(ret) == 0:
                # Should not have recursed twice
                if force_end:
                    raise CannotGenerateLevelError("Could not find valid blocks and end forcing causes recursion")
                return self._get_valid_blocks(current_spot, lvl, placed_start, placed_end, start_blocks, end_blocks,
                                              dead_end_blocks, other_blocks, other_spots, True)

            return ret

    def _choose_block(self, valid_blocks, current_spot):
        """
        Chooses a random block based on weights
        :param valid_blocks: The list of valid blocks at current_spot
        :param current_spot: The current spot in question
        :return: The chosen block and the spot for that block to go
        """
        weight_sum = 0
        for block in valid_blocks:
            weight_sum += block.weight

        # To choose a random value, subtract from 1 until tmp < random_value
        random_value = 1 - random.random()  # So 1 is included but 0 is not
        tmp = 1
        for block in valid_blocks:
            tmp -= block.weight * 1.0 / weight_sum
            if tmp < random_value:
                return block

        # If we get here due to floating point error, just return a block
        return valid_blocks[0]

    def generate(self):
        """
        Generates and returns the level
        :return: The Level
        """
        # Level object
        if not self.check_size():
            raise CannotGenerateLevelError("Invalid Size ({},{},{})".format(self.size[X], self.size[Y], self.size[Z]))
        lvl = Level(size=self.size)

        # Random generator
        if self.seed is not None:
            random.seed(self.seed)
        else:
            random.seed(None)

        # Separate out block file types
        start_blocks = [block for block in self.block_list if block.block_type == blocks.BlockType.START]
        end_blocks = [block for block in self.block_list if block.block_type == blocks.BlockType.END]
        dead_end_blocks = [block for block in self.block_list if block.block_type == blocks.BlockType.DEAD_END]
        other_blocks = [block for block in self.block_list if block.block_type != blocks.BlockType.START
                        and block.block_type != blocks.BlockType.END and block.block_type != blocks.BlockType.DEAD_END]

        # Must have at least one start, one end, one end, and one other
        if len(start_blocks) < 1:
            raise CannotGenerateLevelError("Must have at least one start block")
        if len(end_blocks) < 1:
            raise CannotGenerateLevelError("Must have at least one end block")
        if len(dead_end_blocks) < 1:
            raise CannotGenerateLevelError("Must have at least one dead end block")
        if len(other_blocks) < 1:
            raise CannotGenerateLevelError("Must have at least one intermediate block")

        # Pick random start location and make that the list of remaining spots list
        remaining_spots = [(random.randint(0, self.size[X] - 1), 0, random.randint(0, self.size[Z] - 1))]
        placed_start = False
        placed_end = False

        # Main logic loop
        while len(remaining_spots) > 0:
            # Choose a random spot
            random.shuffle(remaining_spots)
            current_spot = remaining_spots.pop()

            # Get a list of all valid blocks that could go in that spot
            valid_blocks = self._get_valid_blocks(current_spot, lvl, placed_start, placed_end, start_blocks, end_blocks,
                                                  dead_end_blocks, other_blocks, remaining_spots)

            # Check to make sure that there are valid blocks
            if len(valid_blocks) == 0:
                raise CannotGenerateLevelError("Could not determine a valid block to place at ({},{},{})"
                                               .format(current_spot[X], current_spot[Y], current_spot[Z]))

            # Place a random block from the list
            chosen_block = self._choose_block(valid_blocks, current_spot)
            if chosen_block.block_type == blocks.BlockType.START:
                placed_start = True
                chosen_block.length = 1
            else:
                blist = self._get_connected_block_list(chosen_block, current_spot, lvl)
                prev_len = min(blist, key=(lambda blk: blk.length))
                chosen_block.length = prev_len.length + 1

                # Special cases for some blocks
                if chosen_block.block_type == blocks.BlockType.RAMP:
                    dummy = blocks.RampDummy(orientation=chosen_block.orientation)
                    dummy.length = chosen_block.length
                    lvl.place_block(dummy, (current_spot[X], current_spot[Y] + 1, current_spot[Z]))
                if chosen_block.block_type == blocks.BlockType.END:
                    placed_end = True
                    lvl.length = chosen_block.length

            lvl.place_block(chosen_block, current_spot)

            # Add all empty adjacent spots to the remaining blocks list
            for pos in chosen_block.adjacent(current_spot):
                if lvl.is_valid(pos) and lvl.is_empty(pos):
                    if pos not in remaining_spots:
                        remaining_spots.append(pos)

        if not placed_end:
            # Last effort, try replacing a dead end with an end
            dead_end_pos = lvl.find_longest_dead_end()
            if dead_end_pos is not None:
                tmp_dead_end = lvl.get_block(dead_end_pos)
                tmp_end = random.choice(end_blocks).make_block(orientation=tmp_dead_end.orientation)
                tmp_end.length = tmp_dead_end.length
                lvl.place_block(tmp_end, dead_end_pos)
                placed_end = True
                lvl.length = tmp_end.length
            else:
                raise CannotGenerateLevelError("Could not place end block")

        return lvl
