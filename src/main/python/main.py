from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QAction
from PyQt5 import Qt

import os, sys
from pathlib import Path

from pyqtconfig import ConfigManager, ConfigDialog


class DesorptionLaserControlGUI(QMainWindow):
    """GUI for controlling the desorption laser automatically and by itself."""

    def __init__(self):
        """Initialize software."""
        super(DesorptionLaserControlGUI, self).__init__()

        self.version = "0.1.0"
        self.author = "Reto Trappitsch"

        # initialize default configuration
        self.config = ConfigManager()
        self.init_configuration()

        # window stuff and version
        self.title = "Desorption Laser Control, v" + self.version
        self.width = 600
        self.height = 20

        # initialize menubar and items that are required in subroutines
        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)
        self.init_menubar()

        self.show()

    def init_configuration(self):
        """Create / initialize local configuration."""
        conf_file = Path.home().joinpath(
            "AppData/Roaming/DesorptionLaserControl/config.json"
        )

        default_settings = {
            "PowerControl Port": None,
            "MCS8a DLL": "C:\Windows\System32\DMCS8.DLL",
            "Manual step (deg)": 1.0,
            "Power up (deg)": 0.1,
            "Power down (deg)": 0.1,
            "Power down fast (deg)": 3.0,
            "ROI Min (cps)": 500,
            "ROI Max (cps)": 1500,
            "ROI burst (cps)": 2000,
            "Regulate every (s)": 1,
        }

        metadata = {"ROI Min (cps)": {"preferred_handler": Qt.QDoubleSpinBox}}

        self.config = ConfigManager(default_settings, filename=conf_file)
        self.config.set_many_metadata(metadata)

    def init_menubar(self):
        """Set up the menu bar."""
        # File Menu
        file_menu = self.menubar.addMenu("&File")

        file_menu_exit = QAction("Exit", self)
        file_menu_exit.triggered.connect(self.close)
        file_menu.addAction(file_menu_exit)

        # Settings Menu
        settings_menu = self.menubar.addMenu("&Settings")

        settings_menu_stage = QAction("Select Rotation Stage", self)
        settings_menu_stage.triggered.connect(self.config_rotation_stage)
        settings_menu.addAction(settings_menu_stage)

        settings_menu_config = QAction("Configuration", self)
        settings_menu_config.triggered.connect(self.config_dialog)
        settings_menu.addAction(settings_menu_config)

    def config_dialog(self):
        """Execute the config dialog. """
        config_dialog = ConfigDialog(self.config, self, cols=1)
        config_dialog.setWindowTitle("Settings")
        config_dialog.accepted.connect(lambda: self.config_update(config_dialog.config))
        config_dialog.exec()

    def config_rotation_stage(self):
        """Have user configure / select the COM port for rotation stage."""
        pass

    def config_update(self, update):
        """Update the configuration."""
        self.config.set_many(update.as_dict())
        self.config.save()


if __name__ == "__main__":
    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext
    app = DesorptionLaserControlGUI()
    exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
