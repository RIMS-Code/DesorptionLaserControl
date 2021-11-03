"""Automatically control the desorption laser power."""

from PyQt5.QtCore import QTimer

from mcs8a import MCS8aComm
from power_control import PowerControl


class LaserAutoControl:
    def __init__(
        self,
        parent,
        power: PowerControl,
        mcs8a: MCS8aComm,
        delta_t: float,
        inc_stp: float,
        dec_stp: float,
        dec_emg: float,
        range_min: int,
        range_max: int,
        range_emg: int,
    ):
        """Automatic laser control.

        :param power: Instance of KDC cube for power
        :param mcs8a: Instance of MCS8a
        :param delta_t: How often to check? in seconds
        :param inc_stp: Increase step
        :param dec_stp: Decrease step
        :param dec_emg: Emergency step down
        :param range_min: Minimum range
        :param range_max: Maximum range
        :param range_emg: Emergency range
        """
        self.parent = parent

        self.power = power
        self.power.step_down = dec_stp
        self.power.step_down_em = dec_emg
        self.power.step_up = inc_stp

        self.mcs8a = mcs8a

        self.delta_t = delta_t * 1000

        self.range_min = range_min
        self.range_max = range_max
        self.delta_range = range_max - range_min
        self.range_emg = range_emg

        self._is_running = False

        self.wait_timer = QTimer()

    # Activate / Deactivate #

    def activate(self):
        """Activate auto control."""
        self._is_running = True
        self.wait_timer.timeout.connect(self.do_adjustment)
        self.do_adjustment()

    def deactivate(self):
        """Deactivate auto control."""
        self._is_running = False
        self.wait_timer.stop()
        self.wait_timer.disconnect()
        self.parent.cps_label.setText("")

    def do_adjustment(self):
        """Does an adjustment."""
        if not self._is_running:
            return

        # DO ADJUSTMENT ROUTINE
        current_cps = self.mcs8a.roi_rate
        self.parent._set_cps_label(current_cps)

        # COMPARE
        if current_cps > self.range_emg:  # EMERGENCY TURN DOWN
            self.power.decrease_emergency()
        elif current_cps < self.range_min + self.delta_range / 3:  # regular increase
            self.power.increase()
        elif current_cps > self.range_max - self.delta_range / 3:
            self.power.decrease()

        print("doing a step.")

        # thread out timer
        self.wait_timer.start(self.delta_t)
