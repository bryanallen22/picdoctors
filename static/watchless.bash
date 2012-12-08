#!/bin/bash

# The general case:
#while true;do N=`find -name "*.less" `;inotifywait -qe modify $N ;for f in $N;do lessc $f ${f%.*}.css;done;done

# Just less/picdoctors.less ==> css/picdoctors.css
while true;
    do N=`find -name "*.less" `;
    inotifywait -qe modify $N ;
    lessc less/picdoctors.less > css/picdoctors.css ;
done
