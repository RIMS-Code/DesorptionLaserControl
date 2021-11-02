"""Class to communicate and get data from the MCS8a TDC."""

import ctypes

from datatypes import AcqStatus


class MCS8aComm:
    def __init__(self, dllpath: str = "C:\Windows\System32\DMCS8.DLL"):
        """Initialize MCS8a Comms class."""
        self.dll = ctypes.windll.LoadLibrary(dllpath)

        # empty variables
        self._acquisition_status = None

    @property
    def is_measuring(self) -> bool:
        """Get status if the device is measuring.

        :return: Status of measurement.
        """
        self._acquisition_status()
        return self._acquisition_status.started == 1

    @property
    def range(self) -> int:
        """Get / set the range of the recording.

        :return: Range set.
        """
        return NotImplementedError

    @range.setter
    def range(self, value: int):
        self.dll.RunCmd(0, bytes(f"range={value}", "ascii"))

    @property
    def roi_rate(self) -> float:
        """Get the rate countrate in counts per seconds in the ROI."""
        self._update_acquisition_status()
        return self._acquisition_status.roirate

    # METHODS #
    def _update_acquisition_status(self):
        """Grab the acquisition status and update the class reference."""
        status = AcqStatus()
        self.dll.GetStatusData(ctypes.byref(status), 0)
        self._acquisition_status = status


if __name__ == "__main__":
    tdc = MCS8aComm()
