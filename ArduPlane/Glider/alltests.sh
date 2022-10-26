#!/bin/bash

rm -rf logs

for i in $(seq 1 9); do
   nice ./runtest.py --mission $i --no-ui
   (nice ./graphs/filter.sh test_runs/mission$i.bin &&
    nice ./graphs/graph_logs.py --mission $i test_runs/mission$i-glide.bin &&
    nice ./tocsv.sh test_runs/mission$i-glide.bin) &
done
wait
./graphs/make_index.sh test_runs/mission*glide*bin > test_runs/index.html
