# DesorptionLaserControl

**New features in this release:**

 - Driver for half-wave plate was fixed and degrees are now read and give accurate details on position
 - Motor movement is threaded out such that GUI stays responsive
 - User can select a dark theme for the program
 - Home button moved to menu bar
 - Communications with APT Half-Wave plates is now implemented via USB and not via COM port
 - User can define laser profiles, save them, and easily switch between lasers

**Important**:

If you had a previous version of the program installed, install the new software. Before starting it, go to your user folder and delete the `config.json` file in `AppData\Roaming\DesorptionLaserControl\`. 

**Behind the scenes changes:**

 - Upgrade to PyQt6
