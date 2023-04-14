# IGOS Simulator

This is a simulater code for IGOS (IGRINS control software). It contains two packages: one to simulate TCS, one to simulate H2RG detectors.

Once you clone this repository, you need to setup a directory for the testing purpose. IGOS by default uses "/IGRINS" directory to store observed fits files, logs, etc. Also, file systems from the computer that is connected to the H2RG are remotely mounted under the "/Volumes". The simulator will need to write files to those directories or any other directory you choose. For the testing purporse, I recommend to use other directory. Lets assume that we are going to use /IGRINS/TEST and /IGRINS/TEST/Volumes.

In case you will be testing a current stable version of IGOS, note that these directory paths are hard coded. So you should use "/IGRINS" and "/Volumes". For the development version of IGOS, this can be customizable.

First create a directory "/IGRINS/TEST". In the cloned repository, you will see a file named "IGRINS_Skeleton.tgz". Untar the contents of this file under "/IGRINS/TEST". The contents of the directory will look like this.

```
> ls /IGRINS/TEST
Config  FITS  Log  obsdata  Volumes
```

You need to edit "/IGRINS/TEST/Config/IGRINS_test.ini" file. By default, it will look like below. If you are setting this in other directory than "/IGRINS/TEST", you need to change the value of "root_path" and "volumes_path" accordingly.

```
[DEFAULT]
root_path = /IGRINS/TEST
volumes_path = /IGRINS/TEST/Volumes

[DT]
sdch-ip = localhost
sdch-port = 5005
sdck-ip = localhost
sdck-port = 5006

[SC]
sdcs-ip = localhost
sdcs-port = 5004
tcs-ip = localhost
tcs-port = 22401
```

Other values should be good assuming that you are running the simulator and IGOS in a same machine.

To launch simulator, first change diretory where you cloned the simulator code. You need to run two commands and it is better to open terminal for each one.

## TCS simulator

```
> python run_tcs_simul.py /IGRINS/TEST/Config tcsbuf.dat
```

Change the first parameter if you are not using "/IGRINS/TEST" directory. The second argument is the name of the file that contains the messages that will be returned by the TCS simulator.

IGOS needs the TCS to understand two commands, one to move the telescope and the other to query the current status of the telescope (coordinate, etc.). The simulator simply ignores the telescope move command, and for the quering command, it simply returns an information in the "tcsbuf.dat" file one at a time.

To quit the simulator, just type "control-c".

## Detector simulator

In another terminal,

```
python run_detector_simulator.py /IGRINS/TEST/Config
```

It will simulate three computers that are connected to three detectors (H, K and S; H-band, K-band and Slit-view camera respectively).

By default, it will read contents of "h_fits.list", "k_fits.list" and "s_fits.list" which are plain text files that contains the names of fits file that will be sent to simulate the detector.

To quit, type "enter".

