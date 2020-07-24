"""
mayalevel.py
Asmita Chitale
Assignment 03
ATCM 3311.0U1
07/24/2020
"""


#====================================================== IMPORTS =======================================================#
import blocks
import level

import logging
import maya.OpenMayaUI as omui
import pymel.core.general as pmcg
import pymel.core.system as pmcs
import PySide2
import shiboken2


#====================================================== CONSTS ========================================================#
X = 0  # Element of size tuple
Y = 1  # Element of size tuple
Z = 2  # Element of size tuple
DEFAULT_BLOCK_SIZE = (10.0, 5.0, 10.0)  # Default dimensions for a unit block in Maya
DEFAULT_GROUP_NAME = "groupBlock"  # Default name for the group to look for within the Maya scenes
LOG = logging.getLogger(__name__)
MAXIMUM_BLOCK_DIMENSION = 1e6  # The code has no maximum, but for the sake of the UI, we should set one
MAXIMUM_BLOCK_PRECISION = 2  # The code has no maximum, but for the sake of the UI, we should set one
MAXIMUM_SIZE = (50, 10, 50)  # The code has no maximum, but for the sake of running quickly, we should set one
MAXIMUM_LENGTH = MAXIMUM_SIZE[X] * MAXIMUM_SIZE[Y] * MAXIMUM_SIZE[Z]  # Longest possible path
MAXIMUM_WEIGHT_DIMENSION = 1e6  # The code has no maximum, but for the sake of the UI, we should set one
MAXIMUM_WEIGHT_PRECISION = 2  # The code has no maximum, but for the sake of the UI, we should set one
VALID_BLOCK_TYPES = (  # List of block types to request in the UI
    blocks.BlockType.START,
    blocks.BlockType.END,
    blocks.BlockType.DEAD_END,
    blocks.BlockType.STRAIGHT,
    blocks.BlockType.RAMP,
    blocks.BlockType.T_INTERSECTION,
    blocks.BlockType.CROSS,
    blocks.BlockType.CURVED,
)


#===================================================== FUNCTIONS =======================================================#
def maya_main_window():
    """Return the maya main window widget"""
    main_window = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(main_window), PySide2.QtWidgets.QWidget)


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
        # Clear the scene for the level
        pmcs.newFile(force=True)

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


class MayaSceneLevelGeneratorUI(PySide2.QtWidgets.QDialog):
    """Maya Scene Level Generator UI Class. Is the View"""

    def __init__(self):
        """Constructor, take needed actions"""
        # Passing the class make this Python 2 and Python 3 compatible
        super(MayaSceneLevelGeneratorUI, self).__init__(parent=maya_main_window())

        # Create the generators needed
        self._level_gen = level.LevelGenerator([blocks.BlockFile("", blk_type) for blk_type in VALID_BLOCK_TYPES])
        self._scene_gen = MayaSceneLevelGenerator(None)  # Fill in level at button press time

        # Window things
        self.setWindowTitle("Maya Scene Level Generator")
        self.resize(500, 200)
        self.setWindowFlags(self.windowFlags() ^ PySide2.QtCore.Qt.WindowContextHelpButtonHint)

        # Set up for the first time
        self._create_widgets()
        self._create_layout()
        self._refresh_view()
        self._create_connections()  # Order matters, since refreshing triggers connections

        print(self._level_gen.block_list)  # TODO delete

    def _refresh_view(self):
        """
        Refreshes the window with new data
        :param from_spinbox: Whether this request is coming from a spinbox. If so, no need to update spinboxes
        :return: None
        """
        # Level Size
        self._level_size_x_spinbox.setValue(self._level_gen.size[X])
        self._level_size_y_spinbox.setValue(self._level_gen.size[Y])
        self._level_size_z_spinbox.setValue(self._level_gen.size[Z])

        # Minimum Length
        self._minimum_length_checkbox.setChecked(self._level_gen.minimum_length is not None)
        self._minimum_length_spinbox.setValue(self._level_gen.minimum_length
                                              if self._level_gen.minimum_length is not None else 0)
        self._minimum_length_spinbox.setEnabled(self._level_gen.minimum_length is not None)

        # Maximum Length
        self._maximum_length_checkbox.setChecked(self._level_gen.maximum_length is not None)
        self._maximum_length_spinbox.setValue(self._level_gen.maximum_length
                                              if self._level_gen.maximum_length is not None else MAXIMUM_LENGTH)
        self._maximum_length_spinbox.setEnabled(self._level_gen.maximum_length is not None)

        # Seed
        self._seed_checkbox.setChecked(self._level_gen.seed is not None)
        self._seed_le.setText(str(self._level_gen.seed) if self._level_gen.seed is not None else "")
        self._seed_le.setEnabled(self._level_gen.seed is not None)

        # Block Size
        self._block_size_x_spinbox.setValue(self._scene_gen.block_dimensions[X])
        self._block_size_y_spinbox.setValue(self._scene_gen.block_dimensions[Y])
        self._block_size_z_spinbox.setValue(self._scene_gen.block_dimensions[Z])

        # Group Name
        self._group_name_le.setText(self._scene_gen.group_name)

        # Object Block List
        for blk_type in VALID_BLOCK_TYPES:
            idx = VALID_BLOCK_TYPES.index(blk_type)
            self._object_blocks[blk_type]["pth_le"].setText(self._level_gen.block_list[idx].pth)
            self._object_blocks[blk_type]["weight_spinbox"].setValue(self._level_gen.block_list[idx].weight)

    def _create_widgets(self):
        """Create widgets for the UI"""
        # Generator Settings Group
        self._generator_group_box = PySide2.QtWidgets.QGroupBox()
        self._generator_group_box.setTitle("Level Generator Settings")

        # Level Size
        self._level_size_lbl = PySide2.QtWidgets.QLabel("Level Size")
        # X
        self._level_size_x_lbl = PySide2.QtWidgets.QLabel("X")
        self._level_size_x_spinbox = PySide2.QtWidgets.QSpinBox()
        self._level_size_x_spinbox.setMinimum(level.MINIMUM_SIZE[X])
        self._level_size_x_spinbox.setMaximum(MAXIMUM_SIZE[X])
        # Y
        self._level_size_y_lbl = PySide2.QtWidgets.QLabel("Y")
        self._level_size_y_spinbox = PySide2.QtWidgets.QSpinBox()
        self._level_size_y_spinbox.setMinimum(level.MINIMUM_SIZE[Y])
        self._level_size_x_spinbox.setMaximum(MAXIMUM_SIZE[Y])
        # Z
        self._level_size_z_lbl = PySide2.QtWidgets.QLabel("Z")
        self._level_size_z_spinbox = PySide2.QtWidgets.QSpinBox()
        self._level_size_z_spinbox.setMinimum(level.MINIMUM_SIZE[Z])
        self._level_size_x_spinbox.setMaximum(MAXIMUM_SIZE[Z])

        # Minimum Length
        self._minimum_length_checkbox = PySide2.QtWidgets.QCheckBox("Minimum Length")
        self._minimum_length_spinbox = PySide2.QtWidgets.QSpinBox()
        self._minimum_length_spinbox.setMinimum(0)  # Negative minimum lengths don't make sense
        self._minimum_length_spinbox.setMaximum(MAXIMUM_LENGTH)  # Minimum lengths > max length doesn't make sense

        # Maximum Length
        self._maximum_length_checkbox = PySide2.QtWidgets.QCheckBox("Maximum Length")
        self._maximum_length_spinbox = PySide2.QtWidgets.QSpinBox()
        self._maximum_length_spinbox.setMinimum(2)  # Maximum lengths < 2 don't make sense
        self._maximum_length_spinbox.setMaximum(MAXIMUM_LENGTH)  # Maximum lengths > max length doesn't make sense

        # Seed
        self._seed_checkbox = PySide2.QtWidgets.QCheckBox("Seed")
        self._seed_le = PySide2.QtWidgets.QLineEdit()

        # Scene Settings Group
        self._scene_group_box = PySide2.QtWidgets.QGroupBox()
        self._scene_group_box.setTitle("Maya Scene Settings")

        # Block Size
        self._block_size_lbl = PySide2.QtWidgets.QLabel("Block Size")
        # X
        self._block_size_x_lbl = PySide2.QtWidgets.QLabel("X")
        self._block_size_x_spinbox = PySide2.QtWidgets.QDoubleSpinBox()
        self._block_size_x_spinbox.setMinimum(0)
        self._block_size_x_spinbox.setMaximum(MAXIMUM_BLOCK_DIMENSION)
        self._block_size_x_spinbox.setDecimals(MAXIMUM_BLOCK_PRECISION)
        self._block_size_x_spinbox.setSingleStep(float("1e-{}".format(MAXIMUM_BLOCK_PRECISION)))
        # Y
        self._block_size_y_lbl = PySide2.QtWidgets.QLabel("Y")
        self._block_size_y_spinbox = PySide2.QtWidgets.QDoubleSpinBox()
        self._block_size_y_spinbox.setMinimum(0)
        self._block_size_y_spinbox.setMaximum(MAXIMUM_BLOCK_DIMENSION)
        self._block_size_y_spinbox.setDecimals(MAXIMUM_BLOCK_PRECISION)
        self._block_size_x_spinbox.setSingleStep(float("1e-{}".format(MAXIMUM_BLOCK_PRECISION)))
        # Z
        self._block_size_z_lbl = PySide2.QtWidgets.QLabel("Z")
        self._block_size_z_spinbox = PySide2.QtWidgets.QDoubleSpinBox()
        self._block_size_z_spinbox.setMinimum(0)
        self._block_size_z_spinbox.setMaximum(MAXIMUM_BLOCK_DIMENSION)
        self._block_size_z_spinbox.setDecimals(MAXIMUM_BLOCK_PRECISION)
        self._block_size_x_spinbox.setSingleStep(float("1e-{}".format(MAXIMUM_BLOCK_PRECISION)))

        # Group Name
        self._group_name_lbl = PySide2.QtWidgets.QLabel("Maya Group Name")
        self._group_name_le = PySide2.QtWidgets.QLineEdit()

        # Object Block Group
        self._block_group_box = PySide2.QtWidgets.QGroupBox()
        self._block_group_box.setTitle("Object Block Settings")

        # Object Blocks
        self._object_blocks = dict()
        for blk_type in VALID_BLOCK_TYPES:
            self._object_blocks[blk_type] = dict()
            self._object_blocks[blk_type]["group"] = PySide2.QtWidgets.QGroupBox()
            self._object_blocks[blk_type]["group"].setTitle(blocks.BLOCK_TYPE_STR[blk_type])
            self._object_blocks[blk_type]["group"].setStyleSheet("QGroupBox{border: 5px solid #444444;}")

            # Path
            self._object_blocks[blk_type]["pth_lbl"] = PySide2.QtWidgets.QLabel("Path")
            self._object_blocks[blk_type]["pth_le"] = PySide2.QtWidgets.QLineEdit()

            # Weight
            self._object_blocks[blk_type]["weight_lbl"] = PySide2.QtWidgets.QLabel("Weight")
            self._object_blocks[blk_type]["weight_spinbox"] = PySide2.QtWidgets.QDoubleSpinBox()
            self._object_blocks[blk_type]["weight_spinbox"].setMinimum(0)
            self._object_blocks[blk_type]["weight_spinbox"].setMaximum(MAXIMUM_WEIGHT_DIMENSION)
            self._object_blocks[blk_type]["weight_spinbox"].setDecimals(MAXIMUM_WEIGHT_PRECISION)
            self._object_blocks[blk_type]["weight_spinbox"].setSingleStep(
                float("1e-{}".format(MAXIMUM_WEIGHT_PRECISION)))

        # Buttons
        self._cancel_btn = PySide2.QtWidgets.QPushButton("Cancel")
        self._generate_btn = PySide2.QtWidgets.QPushButton("Generate")

    def _create_layout(self):
        """Lay out the UI elements"""
        # Level Size
        self._level_size_lay = PySide2.QtWidgets.QHBoxLayout()
        self._level_size_lay.addWidget(self._level_size_lbl)
        self._level_size_lay.addSpacing(10)
        self._level_size_lay.addWidget(self._level_size_x_lbl)
        self._level_size_lay.addWidget(self._level_size_x_spinbox)
        self._level_size_lay.addSpacing(5)
        self._level_size_lay.addWidget(self._level_size_y_lbl)
        self._level_size_lay.addWidget(self._level_size_y_spinbox)
        self._level_size_lay.addSpacing(5)
        self._level_size_lay.addWidget(self._level_size_z_lbl)
        self._level_size_lay.addWidget(self._level_size_z_spinbox)
        self._level_size_lay.addStretch()

        # Minimum Length
        self._minimum_length_lay = PySide2.QtWidgets.QHBoxLayout()
        self._minimum_length_lay.addWidget(self._minimum_length_checkbox)
        self._minimum_length_lay.addSpacing(5)
        self._minimum_length_lay.addWidget(self._minimum_length_spinbox)
        self._minimum_length_lay.addStretch()

        # Minimum Length
        self._maximum_length_lay = PySide2.QtWidgets.QHBoxLayout()
        self._maximum_length_lay.addWidget(self._maximum_length_checkbox)
        self._maximum_length_lay.addSpacing(5)
        self._maximum_length_lay.addWidget(self._maximum_length_spinbox)
        self._maximum_length_lay.addStretch()

        # Seed
        self._seed_lay = PySide2.QtWidgets.QHBoxLayout()
        self._seed_lay.addWidget(self._seed_checkbox)
        self._seed_lay.addSpacing(5)
        self._seed_lay.addWidget(self._seed_le)

        # Generator Settings Group Box
        self._generator_lay = PySide2.QtWidgets.QVBoxLayout()
        self._generator_lay.addLayout(self._level_size_lay)
        self._generator_lay.addLayout(self._minimum_length_lay)
        self._generator_lay.addLayout(self._maximum_length_lay)
        self._generator_lay.addLayout(self._seed_lay)
        self._generator_group_box.setLayout(self._generator_lay)

        # Block Size
        self._block_size_lay = PySide2.QtWidgets.QHBoxLayout()
        self._block_size_lay.addWidget(self._block_size_lbl)
        self._block_size_lay.addSpacing(10)
        self._block_size_lay.addWidget(self._block_size_x_lbl)
        self._block_size_lay.addWidget(self._block_size_x_spinbox)
        self._block_size_lay.addSpacing(5)
        self._block_size_lay.addWidget(self._block_size_y_lbl)
        self._block_size_lay.addWidget(self._block_size_y_spinbox)
        self._block_size_lay.addSpacing(5)
        self._block_size_lay.addWidget(self._block_size_z_lbl)
        self._block_size_lay.addWidget(self._block_size_z_spinbox)
        self._block_size_lay.addStretch()

        # Group Name
        self._group_name_lay = PySide2.QtWidgets.QHBoxLayout()
        self._group_name_lay.addWidget(self._group_name_lbl)
        self._group_name_lay.addSpacing(10)
        self._group_name_lay.addWidget(self._group_name_le)

        # Maya Scene Group Box
        self._scene_lay = PySide2.QtWidgets.QVBoxLayout()
        self._scene_lay.addLayout(self._block_size_lay)
        self._scene_lay.addLayout(self._group_name_lay)
        self._scene_group_box.setLayout(self._scene_lay)

        # Object Blocks
        for blk_type in VALID_BLOCK_TYPES:
            # Path
            self._object_blocks[blk_type]["pth_lay"] = PySide2.QtWidgets.QHBoxLayout()
            self._object_blocks[blk_type]["pth_lay"].addWidget(self._object_blocks[blk_type]["pth_lbl"])
            self._object_blocks[blk_type]["pth_lay"].addSpacing(10)
            self._object_blocks[blk_type]["pth_lay"].addWidget(self._object_blocks[blk_type]["pth_le"])
            
            # Weight
            self._object_blocks[blk_type]["weight_lay"] = PySide2.QtWidgets.QHBoxLayout()
            self._object_blocks[blk_type]["weight_lay"].addWidget(self._object_blocks[blk_type]["weight_lbl"])
            self._object_blocks[blk_type]["weight_lay"].addSpacing(10)
            self._object_blocks[blk_type]["weight_lay"].addWidget(self._object_blocks[blk_type]["weight_spinbox"])
            self._object_blocks[blk_type]["weight_lay"].addStretch()

            # Object Block Group
            self._object_blocks[blk_type]["group_lay"] = PySide2.QtWidgets.QVBoxLayout()
            self._object_blocks[blk_type]["group_lay"].addSpacing(15)
            self._object_blocks[blk_type]["group_lay"].addLayout(self._object_blocks[blk_type]["pth_lay"])
            self._object_blocks[blk_type]["group_lay"].addLayout(self._object_blocks[blk_type]["weight_lay"])
            self._object_blocks[blk_type]["group"].setLayout(self._object_blocks[blk_type]["group_lay"])

        # Object Block Group Box
        self._block_lay = PySide2.QtWidgets.QVBoxLayout()
        for blk_type in VALID_BLOCK_TYPES:
            self._block_lay.addWidget(self._object_blocks[blk_type]["group"])
        self._block_group_box.setLayout(self._block_lay)

        # Buttons
        self._button_lay = PySide2.QtWidgets.QHBoxLayout()
        self._button_lay.addWidget(self._cancel_btn)
        self._block_size_lay.addSpacing(5)
        self._button_lay.addWidget(self._generate_btn)

        # Main
        self._main_lay = PySide2.QtWidgets.QVBoxLayout()
        self._main_lay.addWidget(self._generator_group_box)
        self._main_lay.addWidget(self._scene_group_box)
        self._main_lay.addWidget(self._block_group_box)
        self._main_lay.addLayout(self._button_lay)

        # Set the layout
        self.setLayout(self._main_lay)

    def _create_connections(self):
        """Connect widget signals to slots"""
        # Level Size
        self._level_size_x_spinbox.valueChanged.connect(self._set_x_size)
        self._level_size_y_spinbox.valueChanged.connect(self._set_y_size)
        self._level_size_z_spinbox.valueChanged.connect(self._set_z_size)

        # Minimum Length
        self._minimum_length_checkbox.toggled.connect(self._checked_minimum)
        self._minimum_length_spinbox.valueChanged.connect(self._set_minimum)

        # Maximum Length
        self._maximum_length_checkbox.toggled.connect(self._checked_maximum)
        self._maximum_length_spinbox.valueChanged.connect(self._set_maximum)

        # Seed
        self._seed_checkbox.toggled.connect(self._checked_seed)
        self._seed_le.textEdited.connect(self._set_seed)
        
        # Block Size
        self._block_size_x_spinbox.valueChanged.connect(self._set_x_block_size)
        self._block_size_y_spinbox.valueChanged.connect(self._set_y_block_size)
        self._block_size_z_spinbox.valueChanged.connect(self._set_z_block_size)

        # Group Name
        self._group_name_le.textEdited.connect(self._set_group_name)

        # Object Blocks
        for blk_type in VALID_BLOCK_TYPES:
            self._object_blocks[blk_type]["pth_le"].textEdited.connect(self._object_block_pth(blk_type))
            self._object_blocks[blk_type]["weight_spinbox"].valueChanged.connect(self._object_block_weight(blk_type))

        # Buttons
        self._cancel_btn.clicked.connect(self._cancel)
        self._generate_btn.clicked.connect(self._generate)

    def _block_signals(self):
        """Block signals while updating info"""
        self._minimum_length_spinbox.blockSignals(True)
        self._maximum_length_spinbox.blockSignals(True)
        self._seed_le.blockSignals(True)

    def _unblock_signals(self):
        """Unblock signals after updating info"""
        self._minimum_length_spinbox.blockSignals(False)
        self._maximum_length_spinbox.blockSignals(False)
        self._seed_le.blockSignals(False)

    @PySide2.QtCore.Slot()
    def _set_x_size(self):
        """Sets the X dimension of the level size"""
        self._level_gen.size = (self._level_size_x_spinbox.value(),
                                self._level_gen.size[Y],
                                self._level_gen.size[Z])
        self._refresh_view()

    @PySide2.QtCore.Slot()
    def _set_y_size(self):
        """Sets the Y dimension of the level size"""
        self._level_gen.size = (self._level_gen.size[X],
                                self._level_size_y_spinbox.value(),
                                self._level_gen.size[Z])
        self._refresh_view()

    @PySide2.QtCore.Slot()
    def _set_z_size(self):
        """Sets the Z dimension of the level size"""
        self._level_gen.size = (self._level_gen.size[X],
                                self._level_gen.size[Y],
                                self._level_size_z_spinbox.value())
        self._refresh_view()

    @PySide2.QtCore.Slot()
    def _checked_minimum(self):
        """Toggles whether a minimum value is set"""
        self._block_signals()
        if self._minimum_length_checkbox.isChecked():
            # Minimum length enabled
            self._level_gen.minimum_length = 0
        else:
            # Minimum length disabled
            self._level_gen.minimum_length = None
        self._refresh_view()
        self._unblock_signals()

    @PySide2.QtCore.Slot()
    def _set_minimum(self):
        """Sets the minimum length"""
        self._level_gen.minimum_length = self._minimum_length_spinbox.value()
        self._refresh_view()

    @PySide2.QtCore.Slot()
    def _checked_maximum(self):
        """Toggles whether a maximum value is set"""
        self._block_signals()
        if self._maximum_length_checkbox.isChecked():
            # Maximum length enabled
            self._level_gen.maximum_length = MAXIMUM_LENGTH
        else:
            # Maximum length disabled
            self._level_gen.maximum_length = None
        self._refresh_view()
        self._unblock_signals()

    @PySide2.QtCore.Slot()
    def _set_maximum(self):
        """Sets the maximum length"""
        self._level_gen.maximum_length = self._maximum_length_spinbox.value()
        self._refresh_view()

    @PySide2.QtCore.Slot()
    def _checked_seed(self):
        """Toggles whether a seed is set"""
        self._block_signals()
        if self._seed_checkbox.isChecked():
            # Seed enabled
            self._level_gen.seed = ""
        else:
            # Seed disabled (use random seed)
            self._level_gen.seed = None
        self._refresh_view()
        self._unblock_signals()

    @PySide2.QtCore.Slot()
    def _set_seed(self):
        """Sets the seed"""
        self._level_gen.seed = self._seed_le.text()
        self._refresh_view()

    @PySide2.QtCore.Slot()
    def _set_x_block_size(self):
        """Sets the X dimension of the block size"""
        self._scene_gen.block_dimensions = (self._block_size_x_spinbox.value(),
                                            self._scene_gen.block_dimensions[Y],
                                            self._scene_gen.block_dimensions[Z])
        self._refresh_view()

    @PySide2.QtCore.Slot()
    def _set_y_block_size(self):
        """Sets the Y dimension of the block size"""
        self._scene_gen.block_dimensions = (self._scene_gen.block_dimensions[X],
                                            self._block_size_y_spinbox.value(),
                                            self._scene_gen.block_dimensions[Z])
        self._refresh_view()

    @PySide2.QtCore.Slot()
    def _set_z_block_size(self):
        """Sets the Z dimension of the block size"""
        self._scene_gen.block_dimensions = (self._scene_gen.block_dimensions[X],
                                            self._scene_gen.block_dimensions[Y],
                                            self._block_size_z_spinbox.value())
        self._refresh_view()

    @PySide2.QtCore.Slot()
    def _set_group_name(self):
        """Sets the group name for reading the Maya scene files"""
        self._scene_gen.group_name = self._group_name_le.text()
        self._refresh_view()

    def _object_block_pth(self, blk_type):
        """
        Returns the Slot for editing an object block's path
        :param blk_type: The block type
        :return: The Slot
        """
        @PySide2.QtCore.Slot()
        def inner_slot():
            idx = VALID_BLOCK_TYPES.index(blk_type)
            self._level_gen.block_list[idx].pth = self._object_blocks[blk_type]["pth_le"].text()
            self._refresh_view()
        return inner_slot

    def _object_block_weight(self, blk_type):
        """
        Returns the Slot for editing an object block's weight
        :param blk_type: The block type
        :return: The Slot
        """
        @PySide2.QtCore.Slot()
        def inner_slot():
            idx = VALID_BLOCK_TYPES.index(blk_type)
            self._level_gen.block_list[idx].weight = self._object_blocks[blk_type]["weight_spinbox"].value()
            self._refresh_view()
        return inner_slot

    @PySide2.QtCore.Slot()
    def _cancel(self):
        """Quits the dialog"""
        self.close()

    @PySide2.QtCore.Slot()
    def _generate(self):
        """Generates the level"""
        # Try to generate level and report errors
        try:
            self._scene_gen.lvl = self._level_gen.generate()
            self._scene_gen.generate()
        except level.CannotGenerateLevelError as err:
            LOG.error(err.message)

        # Give warning if minimum length not met
        if self._scene_gen.lvl.length < self._level_gen.minimum_length:
            LOG.warn("Level length {} is less than desired minimum {}".format(self._scene_gen.lvl.length,
                                                                              self._level_gen.minimum_length))
