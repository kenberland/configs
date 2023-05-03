#!/bin/sh
logger "Running $0"
ID=eDP
LAPTOP=$(xrandr | grep $ID |cut -d\  -f1)
EXTERNAL=$(xrandr | grep -v $ID |grep \ connected | cut -d\  -f1)
xrandr --output $LAPTOP --auto --output $EXTERNAL --off
