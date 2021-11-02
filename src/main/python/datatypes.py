"""Fastcomtec data types.

These data types are copied from Qudi, https://github.com/Ulm-IQO/qudi.
Their fastcomtec MCS6 class defines the same data types that we need here.
"""


import ctypes


class AcqStatus(ctypes.Structure):
    """Create a structured Data type with ctypes where the dll can write into.
    This object handles and retrieves the acquisition status data from the
    Fastcomtec.
    int started;                // acquisition status: 1 if running, 0 else
    double runtime;             // running time in seconds
    double totalsum;            // total events
    double roisum;              // events within ROI
    double roirate;             // acquired ROI-events per second
    double nettosum;            // ROI sum with background subtracted
    double sweeps;              // Number of sweeps
    double stevents;            // Start Events
    unsigned long maxval;       // Maximum value in spectrum
    """

    _fields_ = [
        ("started", ctypes.c_int),
        ("runtime", ctypes.c_double),
        ("totalsum", ctypes.c_double),
        ("roisum", ctypes.c_double),
        ("roirate", ctypes.c_double),
        ("ofls", ctypes.c_double),
        ("sweeps", ctypes.c_double),
        ("stevents", ctypes.c_double),
        ("maxval", ctypes.c_ulong),
    ]


class AcqSettings(ctypes.Structure):
    _fields_ = [
        ("range", ctypes.c_long),
        ("cftfak", ctypes.c_long),
        ("roimin", ctypes.c_long),
        ("roimax", ctypes.c_long),
        ("nregions", ctypes.c_long),
        ("caluse", ctypes.c_long),
        ("calpoints", ctypes.c_long),
        ("param", ctypes.c_long),
        ("offset", ctypes.c_long),
        ("xdim", ctypes.c_long),
        ("bitshift", ctypes.c_ulong),
        ("active", ctypes.c_long),
        ("eventpreset", ctypes.c_double),
        ("dummy1", ctypes.c_double),
        ("dummy2", ctypes.c_double),
        ("dummy3", ctypes.c_double),
    ]


class ACQDATA(ctypes.Structure):
    """Create a structured Data type with ctypes where the dll can write into.
    This object handles and retrieves the acquisition data of the Fastcomtec.
    """

    _fields_ = [
        ("s0", ctypes.POINTER(ctypes.c_ulong)),
        ("region", ctypes.POINTER(ctypes.c_ulong)),
        ("comment", ctypes.c_char_p),
        ("cnt", ctypes.POINTER(ctypes.c_double)),
        ("hs0", ctypes.c_int),
        ("hrg", ctypes.c_int),
        ("hcm", ctypes.c_int),
        ("hct", ctypes.c_int),
    ]


class BOARDSETTING(ctypes.Structure):
    _fields_ = [
        ("sweepmode", ctypes.c_long),
        ("prena", ctypes.c_long),
        ("cycles", ctypes.c_long),
        ("sequences", ctypes.c_long),
        ("syncout", ctypes.c_long),
        ("digio", ctypes.c_long),
        ("digval", ctypes.c_long),
        ("dac0", ctypes.c_long),
        ("dac1", ctypes.c_long),
        ("dac2", ctypes.c_long),
        ("dac3", ctypes.c_long),
        ("dac4", ctypes.c_long),
        ("dac5", ctypes.c_long),
        ("fdac", ctypes.c_int),
        ("tagbits", ctypes.c_int),
        ("extclk", ctypes.c_int),
        ("maxchan", ctypes.c_long),
        ("serno", ctypes.c_long),
        ("ddruse", ctypes.c_long),
        ("active", ctypes.c_long),
        ("holdafter", ctypes.c_double),
        ("swpreset", ctypes.c_double),
        ("fstchan", ctypes.c_double),
        ("timepreset", ctypes.c_double),
    ]
