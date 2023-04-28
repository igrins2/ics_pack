#!/bin/bash

HOME=/home/ics

PYTHONBIN=$HOME/miniconda3/envs/igos2n/bin/python

source ~/.bash_profile
conda activate igos2n

$PYTHONBIN $HOME/ics_pack/code/InstSeq/InstSeq.py



