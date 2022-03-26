from fbs_runtime.application_context.PyQt6 import ApplicationContext
from PyQt6 import QtCore, QtGui, QtWidgets

import qdarktheme

from pathlib import Path
import sys
from typing import Union

from instruments import units as u
from pyqtconfig import ConfigManager, ConfigDialog
import serial.tools.list_ports

from auto_control import LaserAutoControl
from power_control import PowerControl
from mcs8a import MCS8aComm, FakeMCS8aComm
import workers, widgets


class DesorptionLaserControlGUI(QtWidgets.QMainWindow):
    """GUI for controlling the desorption laser automatically and by itself."""

    def __init__(self):
        """Initialize software."""
        super(DesorptionLaserControlGUI, self).__init__()

        self.use_fake_mcs8a = True

        self.version = "0.3.0"
        self.author = "Reto Trappitsch"

        # threadpool
        self.threadpool = QtCore.QThreadPool()

        # main widget
        self.mainwidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainwidget)

        # main widget
        self.increase_button = QtWidgets.QPushButton("+")
        self.decrease_button = QtWidgets.QPushButton("-")
        self.burst_button = QtWidgets.QPushButton("Burst -")
        self.position_label = QtWidgets.QLabel()
        self.manual_step_edit = QtWidgets.QDoubleSpinBox()
        self.set_position = QtWidgets.QDoubleSpinBox()
        self.goto_button = QtWidgets.QPushButton("GoTo")
        self.auto_checkbox = QtWidgets.QCheckBox("Auto control")
        self.cps_label = QtWidgets.QLabel()

        self.movement_buttons = None
        self._buttons_active = True

        # initialize default configuration
        self.config = None
        self.laser_settings = None
        self.laser_settings_metadata = None
        self.conf_folder = Path.home().joinpath(
            "AppData/Roaming/DesorptionLaserControl/"
        )
        self.laser_conf_folder = self.conf_folder.joinpath("lasers/")

        # communication
        self.mcs8a = None
        self.power = None
        self._power_curr_position = None
        self.auto_control = None

        # window stuff and version
        self.title = "Desorption Laser Control, v" + self.version
        self.width = 600
        self.height = 20

        # initialize menubar and items that are required in subroutines
        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)

        # init all
        self.init_configuration()
        self.init_laser_config()
        self.init_comms()
        self.init_menubar()
        self.init_ui()

        self.show()

    def init_comms(self):
        """Initialize comms."""
        if self.config.get("Port") is None:
            QtWidgets.QMessageBox.warning(
                self,
                "No rotation stage selected",
                "Please select a rotation stage port to control the " "laser power.",
            )
            return

        if not Path(self.config.get("MCS8a DLL")).is_file():
            if self.use_fake_mcs8a:
                QtWidgets.QMessageBox.information(
                    self, "Fake MCS8a", "No MCS8a DLL is present, so I'm faking it..."
                )
                self.mcs8a = FakeMCS8aComm()
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "MCS8a DLL missing",
                    "Please select a valid MCS8a DLL in the settings.",
                )
        else:
            self.mcs8a = MCS8aComm(dllpath=self.config.get("MCS8a DLL"))

        try:
            self.power = PowerControl(self.config.get("Port"), gui=self)
        except TimeoutError:
            QtWidgets.QMessageBox.warning(
                self,
                "Timeout",
                "Communication with the rotation stage timed out. "
                "Please check your settings.",
            )
            return
        except serial.serialutil.SerialException:
            QtWidgets.QMessageBox.warning(
                self,
                "Couldn't communicate",
                "Communication with the rotation failed. "
                "Please check your settings.",
            )
            return

        except IndexError:
            QtWidgets.QMessageBox.warning(
                self,
                "Index Error",
                "It looks like the device you've chosen is not a rotation stage.",
            )
            return

        # get current position
        self.power_curr_position_read()

    def init_configuration(self):
        """Create / initialize local configuration."""
        conf_file = self.conf_folder.joinpath("config.json")

        default_settings = {
            "Port": None,
            "man_step": 0.1,
            "MCS8a DLL": "C:\Windows\System32\DMCS8.DLL",
            "Power up (deg)": 0.1,
            "Power down (deg)": 0.1,
            "Power down fast (deg)": 3.0,
            "ROI Min (cps)": 500,
            "ROI Max (cps)": 1500,
            "ROI burst (cps)": 2000,
            "Regulate every (s)": 3,
            "TDC Channel": 1,
            "Display Precision": 2,
            "GUI Theme": "light",
            "laser_config": "default.json",
        }

        metadata = {
            "Port": {"prefer_hidden": True},
            "man_step": {"prefer_hidden": True},
            "ROI Min (cps)": {"preferred_handler": widgets.LargeQSpinBox},
            "ROI Max (cps)": {"preferred_handler": widgets.LargeQSpinBox},
            "ROI burst (cps)": {"preferred_handler": widgets.LargeQSpinBox},
            "Regulate every (s)": {"preferred_handler": widgets.RegulateEverySpinbox},
            "GUI Theme": {
                "preferred_handler": QtWidgets.QComboBox,
                "preferred_map_dict": {"Dark": "dark", "Light": "light"},
            },
            "TDC Channel": {"prefer_hidden": True},  # fixme
            "laser_config": {"prefer_hidden": True},
        }

        self.config = ConfigManager(default_settings, filename=conf_file)
        self.config.set_many_metadata(metadata)
        self.config.save()

        self._set_theme()

    def init_laser_config(self):
        """Create / initialize the local laser configuration."""
        lconf_file = self.laser_conf_folder.joinpath(
            self.config.get("laser_config")
        ).with_suffix(".json")

        default_lconf = {
            "Laser Name": "default",
            "Lower limit (deg)": 0.0,
            "Upper limit (deg)": 45.0,
            "Write offset to stage & home": False,
            "Zero offset (deg)": 0.0,
            "Current zero offset (deg)": 0.0,
        }

        metadata = {
            "Lower limit (deg)": {"preferred_handler": widgets.AngleQDoubleSpinBox},
            "Upper limit (deg)": {"preferred_handler": widgets.AngleQDoubleSpinBox},
            "Zero offset (deg)": {"preferred_handler": widgets.AngleQDoubleSpinBox},
            "Current zero offset (deg)": {
                "preferred_handler": widgets.ReadOnlyQDoubleSpinBox
            },
        }
        self.laser_settings_metadata = metadata

        self.laser_settings_config_manager(default_lconf, lconf_file, metadata)
        self.laser_settings.save()

    def init_menubar(self):
        """Set up the menu bar."""
        # File Menu
        file_menu = self.menubar.addMenu("&File")

        file_menu_init = QtGui.QAction("Initialize", self)
        file_menu_init.triggered.connect(self.init_comms)
        file_menu.addAction(file_menu_init)

        file_menu_exit = QtGui.QAction("Exit", self)
        file_menu_exit.setShortcut("Ctrl+q")
        file_menu_exit.triggered.connect(self.close)
        file_menu.addAction(file_menu_exit)

        # Stage Menu

        stage_menu = self.menubar.addMenu("&Stage")

        stage_menu_read_pos = QtGui.QAction("Read position", self)
        stage_menu_read_pos.setToolTip("Read current position of stage.")
        stage_menu_read_pos.setShortcut("Ctrl+r")
        stage_menu_read_pos.triggered.connect(self.power_curr_position_read)
        stage_menu.addAction(stage_menu_read_pos)

        stage_menu_home = QtGui.QAction("Home Stage", self)
        stage_menu_home.setToolTip("Home the Stage and set to zero.")
        stage_menu_home.triggered.connect(self.home)
        stage_menu.addAction(stage_menu_home)

        stage_menu_conf = QtGui.QAction("Configure Stage", self)
        stage_menu_conf.setToolTip("Configure the given stage for a specific laser.")
        stage_menu_conf.triggered.connect(self.laser_settings_dialog)
        stage_menu.addSeparator()
        stage_menu.addAction(stage_menu_conf)

        stage_menu_load = QtGui.QAction("Load Configuration", self)
        stage_menu_load.setToolTip("Load an existing stage configuration.")
        stage_menu_load.triggered.connect(self.laser_settings_load)
        stage_menu.addAction(stage_menu_load)

        # Settings Menu
        settings_menu = self.menubar.addMenu("Settings")

        settings_menu_stage = QtGui.QAction("Select Rotation Stage", self)
        settings_menu_stage.triggered.connect(self.config_rotation_stage)
        settings_menu.addAction(settings_menu_stage)

        settings_menu_config = QtGui.QAction("Configuration", self)
        settings_menu_config.triggered.connect(self.config_dialog)
        settings_menu.addAction(settings_menu_config)

    def init_ui(self):
        """Initialize the UI."""

        def hseparator(width: int = 3) -> QtWidgets.QFrame:
            """Create a horizontal separator and return it.

            :param width: linewidth, defaults to 3

            :return: QFrame separator line.
            """
            sep = QtWidgets.QFrame()
            sep.setFrameShape(QtWidgets.QFrame.Shape.VLine)
            sep.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum,
            )
            sep.setLineWidth(width)
            return sep

        def vseparator(width: int = 3) -> QtWidgets.QFrame:
            """Create a separator and return it.

            :param width: linewidth, defaults to 3

            :return: QFrame separator line.
            """
            sep = QtWidgets.QFrame()
            sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            sep.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Expanding,
            )
            sep.setLineWidth(width)
            return sep

        layout = QtWidgets.QVBoxLayout()

        self.mainwidget.setLayout(layout)

        # position label
        pos_font = QtGui.QFont()
        pos_font.setPixelSize(32)
        pos_font.setBold(True)
        self.position_label.setFont(pos_font)
        self.position_label.setToolTip("Current position")

        pos_layout = QtWidgets.QHBoxLayout()
        pos_layout.addStretch()
        pos_layout.addWidget(self.position_label)
        pos_layout.addStretch()
        layout.addLayout(pos_layout)

        layout.addWidget(vseparator())

        # tooltips and shortcuts
        self.decrease_button.setShortcut("-")
        self.decrease_button.setToolTip(
            "Decrase power by set increment\n" "Keyboard shortcut: -"
        )
        self.increase_button.setShortcut("=")
        self.increase_button.setToolTip(
            "Increase power by set increment\n" "Keyboard shortcut: ="
        )
        self.burst_button.setShortcut("0")
        self.burst_button.setToolTip(
            "Burst / emergency decrease power\n" "Keyboard shortcut: 0"
        )

        # set precision / tuning
        self.manual_step_edit.setSingleStep(0.1)

        # increase / decrease / burst

        tmphlay = QtWidgets.QHBoxLayout()
        tmphlay.addWidget(self.decrease_button)
        tmphlay.addWidget(self.manual_step_edit)
        tmphlay.addWidget(self.increase_button)
        layout.addLayout(tmphlay)

        tmphlay = QtWidgets.QHBoxLayout()
        tmphlay.addWidget(self.burst_button)
        layout.addLayout(tmphlay)

        layout.addWidget(vseparator())

        # Go To actions

        goto_zero_button = QtWidgets.QPushButton("Zero")
        goto_zero_button.setShortcut("Ctrl+0")
        goto_zero_button.setToolTip(
            "Move to zero degrees\n" "Keyboard shortcut: Ctrl+0"
        )
        goto_zero_button.clicked.connect(lambda: self.move_stage(0, absolute=True))

        self.set_position.setMinimum(-360)
        self.set_position.setMaximum(360)

        tmphlay = QtWidgets.QHBoxLayout()
        tmphlay.addWidget(goto_zero_button)
        tmphlay.addStretch()
        tmphlay.addWidget(hseparator())
        tmphlay.addStretch()
        tmphlay.addWidget(self.set_position)
        tmphlay.addWidget(self.goto_button)
        layout.addLayout(tmphlay)

        layout.addWidget(vseparator())

        self.movement_buttons = [
            self.increase_button,
            self.decrease_button,
            self.burst_button,
            self.goto_button,
            goto_zero_button,
        ]

        # automatic control

        tmphlay = QtWidgets.QHBoxLayout()
        tmphlay.addWidget(self.auto_checkbox)
        tmphlay.addStretch()
        tmphlay.addWidget(self.cps_label)
        layout.addLayout(tmphlay)

        # setup
        self.config.add_handler("man_step", self.manual_step_edit)
        self.set_position.setValue(0.0)

        # connect
        self.manual_step_edit.valueChanged.connect(lambda x: self.config.save())
        self.increase_button.clicked.connect(self.manual_increase)
        self.decrease_button.clicked.connect(self.manual_decrease)
        self.burst_button.clicked.connect(self.manual_burst_decrease)
        self.auto_checkbox.stateChanged.connect(self.laser_control)
        self.goto_button.clicked.connect(self.goto)

    @property
    def controls_active(self) -> bool:
        """Get if the buttons are active or not.

        :return: Are the buttons active?
        """
        return self._buttons_active

    @controls_active.setter
    def controls_active(self, value: bool):
        for button in self.movement_buttons:
            button.setEnabled(value)
        self.set_position.setEnabled(value)
        self.manual_step_edit.setEnabled(value)
        self._buttons_active = value

    def config_dialog(self):
        """Execute the config dialog."""
        config_dialog = ConfigDialog(self.config, self, cols=1)
        config_dialog.setWindowTitle("Settings")
        config_dialog.accepted.connect(lambda: self.config_update(config_dialog.config))
        config_dialog.exec()

    def config_rotation_stage(self):
        """Have user configure / select the COM port for rotation stage."""
        ports = serial.tools.list_ports.comports()
        ports_list = []
        for port, desc, hwid in sorted(ports):
            ports_list.append(f"{port}: {desc} [{hwid}]")

        item, ok = QtWidgets.QInputDialog.getItem(
            self, "Select port of Rotation Stage", "Ports", ports_list, 0, False
        )

        if ok and item:
            self.config.set("Port", item.split(":")[0])
        self.config.save()
        self.init_comms()

    def config_update(self, update):
        """Update the configuration."""
        self.config.set_many(update.as_dict())
        self._set_theme()
        self.config.save()

    def goto(self):
        """Goto a user set position."""
        pos = self.set_position.value()
        self.move_stage(pos, absolute=True)

    def home(self):
        """Home the stage."""
        timeout = self.power.ch.motion_timeout
        self.power.ch.motion_timeout = 100 * u.sec
        self.power.ch.go_home()
        self.power.ch.motion_timeout = timeout
        self.power_curr_position_read()

    def laser_control(self):
        """Automatic control."""
        # turn on:
        if self.auto_checkbox.isChecked():
            self.auto_control = LaserAutoControl(
                self,
                self.power,
                self.mcs8a,
                self.config.get("Regulate every (s)"),
                self.config.get("ROI Min (cps)"),
                self.config.get("ROI Max (cps)"),
                self.config.get("ROI burst (cps)"),
                self.config.get("TDC Channel"),
            )
            self.auto_control.activate()
        else:  # turn off
            if self.auto_control is not None:
                self.auto_control.deactivate()
            self.auto_control = None

    def laser_settings_config_manager(
        self, conf: dict, fname: str, metadata: dict = None
    ):
        """Create a laser settings config manager with given config and metadata.

        This also saves the config manager.
        If the metadata are not specified, the ones saved in the class will be used.

        :param conf: Configuration for the manager.
        :param fname: File name to save it to.
        :param metadata: Meta data for the configuration manager.
        """
        if metadata is None:
            metadata = self.laser_settings_metadata

        laser_settings_conf = ConfigManager(conf, filename=fname)
        laser_settings_conf.set_many_metadata(metadata)
        self.laser_settings = laser_settings_conf

    def laser_settings_dialog(self):
        """Execute the config dialog."""
        current_offset = self.power.offset.magnitude
        self.laser_settings.set("Current zero offset (deg)", current_offset)

        self.laser_settings.set("Write offset to stage & home", False)

        laser_settings_dialog = ConfigDialog(self.laser_settings, self, cols=2)
        laser_settings_dialog.setWindowTitle("Configure Laser")
        laser_settings_dialog.accepted.connect(
            lambda: self.laser_settings_update(laser_settings_dialog.config)
        )
        laser_settings_dialog.exec()

    def laser_settings_load(self) -> None:
        """Load an existing laser settings file."""
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Laser Settings",
            str(self.laser_conf_folder),
            "JSON FIles (*.json)",
        )[0]

        if fname == "":
            return

        self.laser_settings_config_manager(self.laser_settings.as_dict(), fname)
        self.laser_settings_set_offset(force=True)
        self.config.set("laser_config", self.laser_settings.get("Laser Name"))
        self.config.save()

    def laser_settings_update(self, update):
        """Update the configuration."""
        laser_name = update.as_dict()["Laser Name"]
        self.config.set("laser_config", laser_name)
        self.config.save()

        fname = self.laser_conf_folder.joinpath(laser_name).with_suffix(".json")
        self.laser_settings_config_manager(self.laser_settings.as_dict(), fname)
        self.laser_settings.set_many(update.as_dict())
        self.laser_settings.save()
        self.laser_settings_set_offset()

    def laser_settings_set_offset(self, force: bool = False):
        """Look at laser settings and set offset, if required by user.

        :param force: Force the writing of the parameters and homing?
        """
        write_it = self.laser_settings.get("Write offset to stage & home")
        user_offset = self.laser_settings.get("Zero offset (deg)")
        if write_it or force:
            self.power.offset = user_offset
            self.home()

    def auto_decrease(self):
        """Decrease by automatic step."""
        step = self.config.get("Power down (deg)")
        self.move_stage(-step, absolute=False, is_auto=True)

    def auto_burst_decrease(self):
        """Decrease if burst occured -> fast."""
        self.manual_burst_decrease(is_auto=True)

    def auto_increase(self):
        step = self.config.get("Power up (deg)")
        self.move_stage(step, absolute=False, is_auto=True)

    def manual_decrease(self):
        """Decrease by manual step."""
        step = self.manual_step_edit.value()
        self.move_stage(-step, absolute=False)

    def manual_burst_decrease(self, is_auto=False):
        """Decrease fast by manual burst step."""
        step = self.config.get("Power down fast (deg)")
        self.move_stage(-step, absolute=False, is_auto=True)

    def manual_increase(self):
        """Increase by manual step."""
        step = self.manual_step_edit.value()
        self.move_stage(step, absolute=False)

    def move_stage(
        self, val: float, absolute: bool = True, is_auto: bool = False
    ) -> None:
        """Move stage to an absolute value in degrees.

        During movement, the whole widget is deactivated and subsequently reactivated.

        :param val: Value to do got in degrees.
        :param absolute: Absolute move or not?
        :param is_auto: If we come from auto control, we don't want to turn it off.
        """
        # turn off auto control
        if isinstance(self.auto_control, LaserAutoControl) and not is_auto:
            self.auto_control.deactivate()

        self.controls_active = False
        self.auto_checkbox.setEnabled(False)

        # check limits
        new_position = self.power_curr_position + val
        if new_position < (limit := self.laser_settings.get("Lower limit (deg)")):
            val = limit
            absolute = True
        elif new_position > (limit := self.laser_settings.get("Upper limit (deg)")):
            val = limit
            absolute = True

        # thread out movement
        worker = workers.Worker(self.power.ch.move, val * u.degree, absolute=absolute)
        worker.signals.error.connect(self.move_stage_error)
        worker.signals.movement_finished.connect(self.move_stage_finished)
        self.threadpool.start(worker)

    def move_stage_error(self, msg) -> None:
        """Accept the error of a movement, update the position, and unlock buttons."""
        QtWidgets.QMessageBox.warning(self, "Movement error", msg)
        self.move_stage_finished()

    def move_stage_finished(self) -> None:
        """Update GUI and unlock the buttons after a movement is done."""
        self.power_curr_position_read()
        self.controls_active = True
        self.auto_checkbox.setEnabled(True)

        if isinstance(self.auto_control, LaserAutoControl):
            self.auto_control.activate()

    @property
    def power_curr_position(self):
        """Set / get current position"""
        return self._power_curr_position

    def power_curr_position_read(self):
        """Read current position from Stage and set it to the value in degrees."""
        value = self.power.ch.position.magnitude
        self._power_curr_position = value
        self._set_position_label()

    def _set_position_label(self):
        """Set position label in degrees."""
        prec = self.config.get("Display Precision")
        self.position_label.setText(f"{self.power_curr_position:.{prec}f}\u00B0")

    def _set_cps_label(self, value: Union[int, float]):
        """Set counts per second label."""
        self.cps_label.setText(f"ROI: {int(value)} cps")

    def _set_theme(self):
        """Set the GUI theme."""
        theme = self.config.get("GUI Theme")
        if theme == "dark":
            self.setStyleSheet(qdarktheme.load_stylesheet("dark"))
        else:
            self.setStyleSheet(qdarktheme.load_stylesheet("light"))


if __name__ == "__main__":
    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext
    app = DesorptionLaserControlGUI()
    exit_code = appctxt.app.exec()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
