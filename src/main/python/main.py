from fbs_runtime.application_context.PyQt6 import ApplicationContext
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QComboBox,
    QMainWindow,
    QInputDialog,
    QMessageBox,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QWidget,
)
import qdarktheme

import sys
from pathlib import Path
from typing import Union

from instruments import units as u
from pyqtconfig import ConfigManager, ConfigDialog
import serial.tools.list_ports

from auto_control import LaserAutoControl
from power_control import PowerControl
from mcs8a import MCS8aComm
import widgets


class DesorptionLaserControlGUI(QMainWindow):
    """GUI for controlling the desorption laser automatically and by itself."""

    def __init__(self):
        """Initialize software."""
        super(DesorptionLaserControlGUI, self).__init__()

        self.version = "0.1.0"
        self.author = "Reto Trappitsch"

        # main widget
        self.mainwidget = QWidget()
        self.setCentralWidget(self.mainwidget)

        # main widget
        self.increase_button = QPushButton("+")
        self.decrease_button = QPushButton("-")
        self.position_label = QLabel()
        self.manual_step_edit = QDoubleSpinBox()
        self.set_position = QDoubleSpinBox()
        self.goto_button = QPushButton("GoTo")
        self.auto_checkbox = QCheckBox("Automatic laser control")
        self.cps_label = QLabel()

        # initialize default configuration
        self.config = ConfigManager()

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
        self.init_comms()
        self.init_menubar()
        self.init_ui()

        self.show()

    def init_comms(self):
        """Initialize comms."""
        if self.config.get("Port") is None:
            QMessageBox.warning(
                self,
                "No rotation stage selected",
                "Please select a rotation stage port to control the " "laser power.",
            )
            return

        if not Path(self.config.get("MCS8a DLL")).is_file():
            QMessageBox.warning(
                self,
                "MCS8a DLL missing",
                "Please select a valid MCS8a DLL in the settings.",
            )
        else:
            self.mcs8a = MCS8aComm(dllpath=self.config.get("MCS8a DLL"))

        try:
            self.power = PowerControl(self.config.get("Port"), gui=self)
        except TimeoutError:
            QMessageBox.warning(
                self,
                "Timeout",
                "Communication with the rotation stage timed out. "
                "Please check your settings.",
            )
            return
        except serial.serialutil.SerialException:
            QMessageBox.warning(
                self,
                "Couldn't communicate",
                "Communication with the rotation failed. "
                "Please check your settings.",
            )
            return

        except IndexError:
            QMessageBox.warning(
                self,
                "Index Error",
                "It looks like the device you've chosen is not a rotation stage.",
            )
            return

        # get current position
        self.power_curr_position = self.power.ch.position.magnitude

    def init_configuration(self):
        """Create / initialize local configuration."""
        conf_file = Path.home().joinpath(
            "AppData/Roaming/DesorptionLaserControl/config.json"
        )

        default_settings = {
            "Port": None,
            "man_step": 1.0,
            "MCS8a DLL": "C:\Windows\System32\DMCS8.DLL",
            "Power up (deg)": 0.1,
            "Power down (deg)": 0.1,
            "Power down fast (deg)": 3.0,
            "ROI Min (cps)": 500,
            "ROI Max (cps)": 1500,
            "ROI burst (cps)": 2000,
            "Regulate every (s)": 3,
            "TDC Channel": 1,
            "Display Precision": 3,
            "GUI Theme": "light",
        }

        metadata = {
            "Port": {"prefer_hidden": True},
            "man_step": {"prefer_hidden": True},
            "ROI Min (cps)": {"preferred_handler": widgets.LargeQSpinBox},
            "ROI Max (cps)": {"preferred_handler": widgets.LargeQSpinBox},
            "ROI burst (cps)": {"preferred_handler": widgets.LargeQSpinBox},
            "GUI Theme": {
                "preferred_handler": QComboBox,
                "preferred_map_dict": {"Dark": "dark", "Light": "light"},
            },
            "TDC Channel": {"prefer_hidden": True},  # fixme
        }

        self.config = ConfigManager(default_settings, filename=conf_file)
        self.config.set_many_metadata(metadata)
        self.config.save()

        self._set_theme()

    def init_menubar(self):
        """Set up the menu bar."""
        # File Menu
        file_menu = self.menubar.addMenu("&File")

        file_menu_init = QAction("Initialize", self)
        file_menu_init.triggered.connect(self.init_comms)
        file_menu.addAction(file_menu_init)

        file_menu_exit = QAction("Exit", self)
        file_menu_exit.setShortcut("Ctrl+q")
        file_menu_exit.triggered.connect(self.close)
        file_menu.addAction(file_menu_exit)

        # Stage Menu

        stage_menu = self.menubar.addMenu("&Stage")

        stage_menu_home = QAction("Home Stage", self)
        stage_menu_home.setStatusTip("Home the Stage and set to zero.")
        stage_menu_home.triggered.connect(self.home)
        stage_menu.addAction(stage_menu_home)

        # Settings Menu
        settings_menu = self.menubar.addMenu("Settings")

        settings_menu_stage = QAction("Select Rotation Stage", self)
        settings_menu_stage.triggered.connect(self.config_rotation_stage)
        settings_menu.addAction(settings_menu_stage)

        settings_menu_config = QAction("Configuration", self)
        settings_menu_config.triggered.connect(self.config_dialog)
        settings_menu.addAction(settings_menu_config)

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()

        self.mainwidget.setLayout(layout)

        layout.addWidget(self.position_label)

        tmphlay = QHBoxLayout()
        tmphlay.addWidget(self.decrease_button)
        tmphlay.addStretch()
        tmphlay.addWidget(self.manual_step_edit)
        tmphlay.addStretch()
        tmphlay.addWidget(self.increase_button)
        layout.addLayout(tmphlay)

        tmphlay = QHBoxLayout()
        tmphlay.addWidget(self.set_position)
        tmphlay.addWidget(self.goto_button)
        tmphlay.addStretch()
        layout.addLayout(tmphlay)

        tmphlay = QHBoxLayout()
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
        self.auto_checkbox.stateChanged.connect(self.laser_control)
        self.goto_button.clicked.connect(self.goto)

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

        item, ok = QInputDialog.getItem(
            self, "Select port of Rotation Stage", "Ports", ports_list, 0, False
        )

        if ok and item:
            self.config.set("Port", item.split(":")[0])
        self.config.save()

    def config_update(self, update):
        """Update the configuration."""
        self.config.set_many(update.as_dict())
        self._set_theme()
        self.config.save()

    def goto(self):
        """Goto a user set position."""
        pos = self.set_position.value()
        try:
            self.power.ch.move(pos * u.degree)
        except OSError:
            # fixme: ik has some issue here with received answer
            pass
        self.power_curr_position = pos

    def home(self):
        """Home the stage."""
        try:
            self.power.ch.go_home()
        except OSError:
            # fixme: ik has some issue here with received answer
            pass
        self.power_curr_position = 0

    def laser_control(self):
        """Automatic control."""
        # turn on:
        if self.auto_checkbox.isChecked():
            self.auto_control = LaserAutoControl(
                self,
                self.power,
                self.mcs8a,
                self.config.get("Regulate every (s)"),
                self.config.get("Power up (deg)"),
                self.config.get("Power down (deg)"),
                self.config.get("Power down fast (deg)"),
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

    def manual_decrease(self):
        """Increase by manual step."""
        step = self.manual_step_edit.value()
        try:
            self.power.ch.move(-step * u.degree, absolute=False)
        except OSError:
            # fixme: ik has some issue here with received answer
            pass
        self.power_curr_position -= step

    def manual_increase(self):
        """Increase by manual step."""
        step = self.manual_step_edit.value()
        try:
            self.power.ch.move(step * u.degree, absolute=False)
        except OSError:
            # fixme: ik has some issue here with received answer
            pass
        self.power_curr_position += step

    @property
    def power_curr_position(self):
        """Set / get current position"""
        return self._power_curr_position

    @power_curr_position.setter
    def power_curr_position(self, value):
        self._power_curr_position = value
        self._set_position_label()

    def _set_position_label(self):
        """Set position label in degrees."""
        self.position_label.setText(
            f"Current position: {self.power_curr_position:.3f} deg"
        )

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
