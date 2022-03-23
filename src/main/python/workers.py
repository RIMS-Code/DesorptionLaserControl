"""PyQt runnables for threading out.

This QRunnable and Worker signals follow closely the great tutorial here:
https://www.pythonguis.com/tutorials/multithreading-pyqt6-applications-qthreadpool/
"""


from PyQt6 import QtCore


class WorkerSignals(QtCore.QObject):
    """Defines the signals available from a running worker thread.

    Supported signals are:

    error: Emits the error message as a string, to display in a box.
    movement_finished: Emits a signal when the movement has successfully finished.

    """

    error = QtCore.pyqtSignal(str)
    movement_finished = QtCore.pyqtSignal()


class Worker(QtCore.QRunnable):
    """Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args
        and kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.fn(*self.args, **self.kwargs)
            self.signals.movement_finished.emit()
        except Exception as err:
            self.signals.error.emit(err.args[0])
