#!/bin/bash

if [[ ! -e $HOME/IGRINS ]]; then
    mkdir $HOME/IGRINS
    echo "mkdir"
elif [[ ! -d $HOME/IGRINS ]]; then
    echo $HOME + "/IGRINS already exists but is not a directory" 1>&2
fi


# set IGRINS file
cp -r $HOME/ics_pack/installation/IGRINS $HOME/IGRINS


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
pip install pyside6
pip install PyQt5
pip install pika


# ds9
cp $HOME/ics_pack/installation/ds9 $HOME/IGRINS/


# start services
sudo cp $HOME/ics_pack/installation/subsystems.service /etc/systemd/system/
sudo cp $HOME/ics_pack/installation/InstSeq.service /etc/systemd/system/




