#!/bin/bash

nice ../Tools/autotest/sim_vehicle.py -D -G -S 10 -v ArduPlane -f glider  --add-param-file=glider_test.parm --console --map -N --custom-location=-35.38,149.16,20000.0,45.0 

