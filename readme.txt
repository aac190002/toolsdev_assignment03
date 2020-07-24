toolsdev_assignment03
Asmita Chitale
Assignment 03
ATCM 3311.0U1
07/24/2020


=== EXTERNAL MODULES ===

This script requires external no modules outside of what is included with Maya 2019.2


=== FILE DESCRIPTIONS ===
- scenes - directory for the example scene files used for level generation. The names of the files say the block type
- src - directory for the source code
	- __init__.py - empty file so the script can be imported in PyCharm
	- blocks.py - classes to model and control the generation of blocks that can go in a level
	- level.py - classes to model and control the generation of levels
	- mayalevel.py - classes to control the scene file generation and to show the UI
- .gitignore - list of paths for GitHub to ignore, such as .idea
- github.txt - has a link to the GitHub page for this project
- readme.txt - this file


=== NOTES FOR INSTRUCTOR ===

1. The features in the proposal were implemented as follows:
	a. Object block selection - in the UI, there are places to fill in the path to each type of block and that block's
		corresponding weight. Instead of a list where blocks are added dynamically, I made the list static since the
		existence of those blocks is required. The weighting is implemented as proposed.
	b. Level pathfinding - in the LevelGenerator's generate function, an algorithm is used to incrementally add blocks
		to the level while making sure that each placed block is legal. This is all done in Python for speed, so the
		actual scenes are added later. The maximum length, minimum length, and seed were all implemented as proposed
	c. Level scene generation - in the MayaSceneLevelGenerator's generate function, each block of the level is
		processed (imported, rotated, and moved) as proposed. The saving step is omitted based on your feedback, so
		that the level can be tweaked and re-generated.
2. The model of the level is level.Level and the models for the blocks are in blocks.py
3. The controller for the level is level.LevelGenerator and the controller for the blocks is blocks.BlockFile. The
	controller for scene generation is mayalevel.MayaSceneLevelGenerator
4. The view is mayalevel.MayaSceneLevelGeneratorUI and is a GUI that uses PySide2
