#!/bin/sh
IFACE=$(xrandr | grep \ connected\ | grep -v eDP1 | awk '{print $1}' | tr -d '\n')
xrandr --output eDP1 --off --output $IFACE --mode 1920x1080i --pos 0x0 --rotate normal --output eDP1 --auto
