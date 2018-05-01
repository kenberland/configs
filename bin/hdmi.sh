#!/bin/sh
sleep 100
ID=eDP
LAPTOP=$(xrandr | grep $ID |cut -d\  -f1)
EXTERNAL=$(xrandr | grep \ connected | grep -v $ID | cut -d\  -f1)
xrandr --output $EXTERNAL --auto --output $LAPTOP --off
