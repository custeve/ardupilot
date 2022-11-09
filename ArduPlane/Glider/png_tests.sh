#!/bin/bash

rm -rf png_logs
rm -rf logs
rm -rf kml
mkdir kml

for i in $(seq 1 1); do
   (nice ./runtest_png_1122.py --mission $i --no-ui &&
   nice mavtogpx.py ./png_logs/logs/$(date +%Y-%m-%d)/flight$i/flight.tlog &&
   nice gpsbabel -t -w -i gpx -f ./png_logs/logs/$(date +%Y-%m-%d)/flight$i/flight.tlog.gpx  -o kml,units=m,floating=1,extrude=1 -F ./kml/flight$i.kml) &
#   (nice ./graphs/filter.sh test_runs/mission$i.bin &&
#    nice ./graphs/graph_logs.py --mission $i test_runs/mission$i-glide.bin &&
#    nice ./tocsv.sh test_runs/mission$i-glide.bin) &
done
#wait
#./graphs/make_index.sh test_runs/mission*glide*bin > test_runs/index.html
