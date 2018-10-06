ID=eDP
LAPTOP=$(xrandr | grep $ID |cut -d\  -f1)
EXTERNAL=DP1
xrandr --output $EXTERNAL --auto --output $LAPTOP --off
xinput --set-prop 16 267 3
