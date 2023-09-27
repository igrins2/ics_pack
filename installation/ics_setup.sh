#!/bin/bash

if [[ ! -e $HOME/IGRINS ]]; then
    mkdir $HOME/IGRINS
    echo "mkdir"
elif [[ ! -d $HOME/IGRINS ]]; then
    echo $HOME + "/IGRINS already exists but is not a directory" 1>&2
fi


# set IGRINS directory including configuration file
cp -r $HOME/ics_pack/installation/IGRINS $HOME


# install python library
cd $HOME/ics_pack/installation
bash Miniconda3-latest-Linux-x86_64.sh
export PATH=$HOME/miniconda3/bin:$PATH
source ~/.bash_profile

conda update conda
conda create -n igos2n python=3.9
conda activate igos2n

pip install numpy
pip install astropy
pip install matplotlib
pip install pyside6==6.4.2
pip install PyQt6 or pyqt5
pip install pika
pip install pytz
pip install Pyrebase4
#conda install -c conda-forge cppyy
#python -m pip install cppyy
#STDCXX=11 MAKE_NPROCS=12 pip install cppyy==2.4.2 --verbose cppyy --no-binary=cppyy-cling
STDCXX=11 python -m pip install cppyy==2.4.0 --no-cache-dir --force-reinstall



# ds9
#cp $HOME/ics_pack/installation/ds9 $HOME/IGRINS/


# start services
sudo chmod 744 $HOME/ics_pack/installation/run_InstSeq.sh
sudo chmod 744 $HOME/ics_pack/installation/run_subsystem.sh
sudo cp $HOME/ics_pack/installation/subsystem.service /etc/systemd/system/
sudo cp $HOME/ics_pack/installation/InstSeq.service /etc/systemd/system/




