#!/bin/bash

if [ ! -d bstates ]; then
    echo "You need to put your equilibrated reps in a folder called bstates."
    echo "Each should be called: eq.rst.00X where X is the rep number."
    exit
fi

if [ ! -d rep_segs ]; then
    mkdir rep_segs
else
	read -p "Do you wish to remove rep_segs? Careful, you could lose your data (y/n) " yn
    case $yn in
        [Yy]* ) rm -r rep_segs; mkdir rep_segs; echo "Ready to run MELD!";;
        [Nn]* ) echo "rep_segs was left untouched.";;
        * ) echo "Please answer yes or no.";;
    esac
fi







