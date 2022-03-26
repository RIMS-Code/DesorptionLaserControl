## DesorptionLaserControl, v0.3.0

**New features in this release:**

 - Position is not calculated anymore but read after each move
 - All movements are threaded out and the GUI is locked during movement, in order to not click to hastily
 - If a movement error occurs, an error message will be displayed
 - Laser profiles can now be saved, which includes:
   - Minimum and maximum angles allowed for the current laser
   - Offset can be set: setting offset will home the stage!

**Important**:

If you had a `v0.1.0` of the program installed, install the new software. Before starting it, go to your user folder and delete the `config.json` file in `AppData\Roaming\DesorptionLaserControl\`. 

**Behind the scenes changes:**

 - Features to set offset are incorporated into `instrumentkit`
 - Homing is not threaded out and will set the timeout adequately to not result in an issue
