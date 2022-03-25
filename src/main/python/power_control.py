"""Control the Thorlabs rotation stage for laser power."""


import instruments as ik
from instruments import units as u


class PowerControl:
    """Commands used for this program to control half-wave plate."""

    def __init__(self, port: str, baud: int = 115200, gui=None) -> None:
        """Initializes communication with the rotation stage.

        :param port: Port the rotation stage can be found at.
        :param baud: Baud rate. Standard should be fine.
        """
        # variables
        self._motor_model = "PRM1-Z8"  # stage model, used to do unitful transfers
        self._step_down = 0.1 * u.degree  # regular step down when regulating
        self._step_down_em = 3 * u.degree  # emergency step down when too high
        self._step_up = 0.1 * u.degree  # regular step up when regulating

        # enable communication with cube and set channel
        self.kdc = ik.thorlabs.APTMotorController.open_serial(port, baud=baud)
        self.ch = self.kdc.channel[0]

        self.gui = gui

        self.ch.motor_model = self._motor_model

        # turn off backlash correction
        self.ch.backlash_correction = 0

    @property
    def motor_model(self) -> str:
        """Get / set motor model."""
        return self._motor_model

    @motor_model.setter
    def motor_model(self, value: str):
        self._motor_model = value

    @property
    def offset(self) -> float:
        """Get / set offset in degrees.

        If unitless, degrees are assumed.

        :return: Offset currently set in degrees.
        """
        return self.ch.home_parameters[3]

    @offset.setter
    def offset(self, value: float):
        if not isinstance(value, u.Quantity):
            value *= u.deg  # assume degrees
        self.ch.home_parameters = None, None, None, value

    # METHODS #

    def home(self) -> None:
        """Home the device."""
        self.ch.go_home()


if __name__ == "__main__":
    app = PowerControl("COM3")
