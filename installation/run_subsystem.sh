#!/bin/bash

HOME=/home/ics

PYTHONBIN=$HOME/miniconda3/envs/igos2n/bin/python

source ~/.bash_profile
conda activate igos2n

cd $HOME/giapi-glue-cc/
source defineGiapiglueEnv.sh

cd $HOME/ics_pack/code/SubSystems/
$PYTHONBIN start_sub.py




