#!/bin/bash

jarfile=javaservices/web/target/web-1.0-SNAPSHOT-standalone.jar

if [ ! -f $jarfile ];
then
    cd javaservices
    ./build.sh
    cd -
fi

num_cores=`python -c"import multiprocessing as mp; print mp.cpu_count()"`

java -Dsaffron.numPipelines=$num_cores -jar $jarfile

