#!/bin/bash
SINK=$(su -c "pactl stat" ken | grep ^Default\ Sink | cut -d\  -f3)
su -c"pactl set-sink-volume $SINK -- $1%" ken

