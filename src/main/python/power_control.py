"""Control the Thorlabs rotation stage for laser power."""


import instruments as ik
from instruments import units as u


class PowerControl:
    """Commands used for this program to control half-wave plate.

    Fixme: Some warning is received on Windows when moving... oh well for now
    """

    def __init__(self, port: str, baud: int = 115200) -> None:
        """Initializes communication with the rotation stage.

        Fixme: Incorporate Backlash correction -> turn it off (needs ik incorporation)
        Fixme: Add Offset setting in this software.

        :param port: Port the rotation stage can be found at.
        :param baud: Baud rate. Standard should be fine.
        """
        # variables
        self._motor_model = "PRM1-Z8"  # stage model, used to do unitful transfers
        self._offset = 0 * u.degree
        self._step_down = 0.1 * u.degree  # regular step down when regulating
        self._step_down_em = 3 * u.degree  # emergency step down when too high
        self._step_up = 0.1 * u.degree  # regular step up when regulating

        # enable communication with cube and set channel
        self.kdc = ik.thorlabs.APTMotorController.open_serial(port, baud=baud)
        self.ch = self.kdc.channel[0]

        self.ch.motor_model = self._motor_model

    @property
    def motor_model(self) -> str:
        """Get / set motor model."""
        return self._motor_model

    @motor_model.setter
    def motor_model(self, value: str):
        self._motor_model = value

    @property
    def offset(self) -> float:
        """Get / set offset in degrees."""
        return self._offset

    @offset.setter
    def offset(self, value: float):
        self._offset = abs(value) * u.degree

    @property
    def step_up(self) -> float:
        """Get / set step up in degrees."""
        return self._step_up

    @step_up.setter
    def step_up(self, value: float):
        self._step_up = abs(value) * u.degree

    @property
    def step_down(self) -> float:
        """Get / set step down in degrees."""
        return self._step_down

    @step_down.setter
    def step_down(self, value: float):
        self._step_down = abs(value) * u.degree

    @property
    def step_down_em(self) -> float:
        """Get / set step down_em in degrees."""
        return self._step_down_em

    @step_down_em.setter
    def step_down_em(self, value: float):
        self._step_down_em = abs(value) * u.degree

    # METHODS #

    def decrease(self) -> None:
        """Decrease by one step."""
        self.ch.move(-self._step_down, absolute=False)

    def decrease_emergency(self) -> None:
        """Decrease by emergency step."""
        self.ch.move(-self._step_down_em, absolute=False)

    def home(self) -> None:
        """Home the device."""
        self.ch.go_home()

    def increase(self) -> None:
        """Increases by one step."""
        self.ch.move(self._step_up, absolute=False)


if __name__ == "__main__":
    app = PowerControl("COM3")
