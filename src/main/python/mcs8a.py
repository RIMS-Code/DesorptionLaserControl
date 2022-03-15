"""Class to communicate and get data from the MCS8a TDC."""

import ctypes

from datatypes import AcqStatus


class MCS8aComm:
    def __init__(self, dllpath: str = "C:\Windows\System32\DMCS8.DLL"):
        """Initialize MCS8a Comms class."""
        self.dll = ctypes.windll.LoadLibrary(dllpath)

        self._active_channel = 0

        # empty variables
        self._acquisition_status = None

    @property
    def acquisition_status(self):
        """Get the acquisition status."""
        return self._acquisition_status

    @property
    def active_channel(self) -> int:
        """Get / set the active channel (starts counting at zero!)"""
        return self._active_channel

    @active_channel.setter
    def active_channel(self, value: int):
        self._active_channel = value

    @property
    def is_measuring(self) -> bool:
        """Get status if the device is measuring.

        :return: Status of measurement.
        """
        self._update_acquisition_status()
        return self._acquisition_status.started == 1

    @property
    def range(self) -> int:
        """Get / set the range of the recording.

        :return: Range set.
        """
        raise NotImplementedError

    @range.setter
    def range(self, value: int):
        self.dll.RunCmd(0, bytes(f"range={value}", "ascii"))

    @property
    def roi_rate(self) -> float:
        """Get the rate countrate in counts per seconds in the ROI."""
        self._update_acquisition_status()
        # todo: not sure why, but this seems to be the ROI Rate! check data structure
        return self._acquisition_status.ofls

    # METHODS #
    def _update_acquisition_status(self):
        """Grab the acquisition status and update the class reference."""
        status = AcqStatus()
        self.dll.GetStatusData(ctypes.byref(status), ctypes.c_int(self.active_channel))
        self._acquisition_status = status


class FakeMCS8aComm:
    """A fake MCS8a instrument that can return some data."""

    def __init__(self):
        """Initialize fake MCS8a."""
        self._active_channel = 0
        # empty variables
        self._acquisition_status = None

    @property
    def acquisition_status(self):
        """Get the acquisition status."""
        return self._acquisition_status

    @property
    def active_channel(self) -> int:
        """Get / set the active channel (starts counting at zero!)"""
        return self._active_channel

    @active_channel.setter
    def active_channel(self, value: int):
        self._active_channel = value

    @property
    def is_measuring(self) -> bool:
        """Get status if the device is measuring.

        :return: We are measuring!
        """
        return True

    @property
    def range(self) -> int:
        """Get / set the range of the recording.

        :return: Range set.
        """
        raise NotImplementedError

    @range.setter
    def range(self, value: int):
        print(f"Set range with value: {value}")

    @property
    def roi_rate(self) -> float:
        """Get the rate countrate in counts per seconds in the ROI."""
        return 500.2


if __name__ == "__main__":
    tdc = MCS8aComm()
