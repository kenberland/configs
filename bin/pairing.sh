#!/bin/sh
IFACE=$(xrandr | grep \ connected\ | grep -v eDP-1 | awk '{print $1}' | tr -d '\n')
xrandr --output $IFACE --auto --output eDP-1 --auto
