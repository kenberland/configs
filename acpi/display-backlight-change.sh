#!/bin/bash
if [[ $1 == "up" ]]; then
    DISPLAY=:0 /usr/bin/xbacklight -inc 10
else
    DISPLAY=:0 /usr/bin/xbacklight -dec 10
fi


