"""My own implementations of PyQt widgets, small tweaking of existing ones."""

from PyQt6 import QtWidgets


class LargeQSpinBox(QtWidgets.QSpinBox):
    """Large QSpinBox with a max of 99999 instead of 99."""

    def __init__(self, parent=None):
        """Initialize the spin box with new settings."""
        super().__init__(parent)
        self.setMaximum(99999)


class AngleQDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    """Create a QDoubleSpinBox that can go plus / minus a full rotation."""

    def __init__(self, parent=None):
        """Initialize the spin box with new settings."""
        super().__init__(parent)
        self.setMinimum(-360)
        self.setMaximum(360)


class ReadOnlyQDoubleSpinBox(AngleQDoubleSpinBox):
    """Create a read only QDoubleSpinBox."""

    def __init__(self, parent=None):
        """Initialize the spin box with new settings."""
        super().__init__(parent)
        self.setEnabled(False)
