#!/bin/sh
logger "elitebook-dock.sh"
xrandr -d :0.0 --output eDP-1 --off --output DP-2-2 --auto
/home/local/ANT/berlandk/configs/bin/configure-xorg
