#!/bin/sh
logger "elitebook-dock.sh"
xrandr -d :0.0 --output eDP1 --off --output DP1-1 --auto
/home/local/ANT/berlandk/configs/bin/configure-xorg
