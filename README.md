# DesorptionLaserControl
Desorption laser control depending on TDC countrate

## Installation

Use the installer provided in releases.
Note that this program only works on Windows,
since it uses the MCS8a DLL in order
to interact with the TDC.
Simply execute the installer.

Currently,
only Thorlabs rotation mounts 
are supported for power control.
The software will only find 
the rotation mount if you enable it
in your device manager with a
virtual COM port.
Please see
[this link](https://www.eltima.com/virtual-com-port-windows-10/)
for more information on how
to set up such a COM port.

## Setup

Upon first starting the software,
select the right COM port by choosing
Settings -> Select Rotation Stage.
After selecting the stage, 
click File -> Initialize to establish
communication with the stage.
Next got to Settings -> Configuration
to check your configuration.
Adopt the values to your liking.
Most likely, 
you won't have to change the location
of the MCS8a DLL, 
and if you do have to the program should tell you.
Hit Ok when you are done and all 
the configurations will be saved,
including the COM port selected
for the stage. 
The configuration will be saved in:
`$HOME/AppData/Roaming/DesorptionLaserControl/config.json`
You can edit this file manually,
however if you break the software, 
just delete the file and start anew.



## Usage

Note: Not much debugging has been done
at the moment.
Be cautious and don't click to fast
when increasing / decreasing
the half-wave plate manually.


When manually increasing / decreasing the rotation stage settings,
take it slow. There is no read feedback at the moment
from the stage.
If you click to fast,
the current position display 
will be out of sync.
If you go to a specific position or home the stage,
you will regain the sync.

Automatic laser controll has a total of 6 settings.
"Power up (deg)", "Power down (deg)", and "Power down fast (deg)"
are the steps it will take with the stage (in degrees) 
to increase, decrease,
or decrease fast when a burst is detected.
The range it will try to be in is between "ROI Min (cps)"
and "ROI Max (cps)".
If the count rate is in or below the lower third of this area,
it will increase the laser power by the selected power up steps.
If it is in the upper third of this region,
the power will be decreased with the "Power down" steps.
"ROI burst (cps)" defines a burst.
If the count rate exceeds this level,
the program will down regulate 
using the fast step.
"Regulate every (s)" defines how often it regulates.
Three seconds is a good value here,
try not to go too fast.

You can manually control the half-wave plate
when the automatic control is on,
however, 
there's a good chance that the sync will be lost
between the current position displayed and the 
actual current position.
If this is acceptable for you,
feel free to click around as much as you like.

Finally, 
the signal that currently has to be
in channel 1 of the TDC.
For no obvious reasons,
other TDC channels don't seem to respond.



## Requirements to run and package

To run this program,
install the packages that are specified in 
`src/requirements/base.txt`
To do so via `pip`, run:
```
pip install -r src/requirements/base.txt
```

Packaging might work with regular fbs
using python 3.6,
however,
has only been tested with fbs professional.
It has been omitted from the requirements file
and needs to be installed separately.