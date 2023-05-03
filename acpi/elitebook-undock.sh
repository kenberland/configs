#!/bin/sh
logger "Running $0"
sleep 0.5
xrandr -d :0.0 --output eDP-1 --auto --output DP-2-2 --off
