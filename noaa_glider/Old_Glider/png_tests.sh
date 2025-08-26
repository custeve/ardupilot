#!/bin/bash
if [ $# -eq 0 ]; then
    rm -rf png_test
    rm -rf logs
fi

rm -rf kml
mkdir kml

for i in $(seq 1 3); do
    if [ $# -eq 0 ]; then
        cp -rf ./missions_png_1122/wind$i.lua ./scripts/wind.lua
        nice ./runtest_png_1122.py --mission $i --no-ui
    fi
   
   nice mavtogpx.py ./png_test/logs/$(date +%Y-%m-%d)/flight$i/flight.tlog
   nice gpsbabel -t -w -i gpx -f ./png_test/logs/$(date +%Y-%m-%d)/flight$i/flight.tlog.gpx  -o kml,units=m,line_color=FF00FFFF,floating=1,extrude=0,points=0,lines=1,tracks=1,trackdata=0 -F ./kml/flight$i.kml
   sed -i "s/<name>GPS device/<name>Flight $i Autopilot Simulation/" kml/flight$i.kml
   sed -i "s/<snippet\/>/<name>Flight $i Track<\/name>/" kml/flight$i.kml
#   (nice ./graphs/filter.sh test_runs/mission$i.bin &&
#    nice ./graphs/graph_logs.py --mission $i test_runs/mission$i-glide.bin &&
#    nice ./tocsv.sh test_runs/mission$i-glide.bin) &
done
#wait
#./graphs/make_index.sh test_runs/mission*glide*bin > test_runs/index.html
