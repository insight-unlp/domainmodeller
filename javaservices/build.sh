#!/bin/bash
cd termextraction/gate
mvn install
cd ../../
mvn install -pl web -am
