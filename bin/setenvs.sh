#!/bin/bash

export PERF_PREFIX='/dash_app/nxn_performance'

alias nxn_perf="python ${PERF_PREFIX}/bin/run_seq.py"

find ./ -name '*.tp' | xargs dos2unix

find ./ -name '*.cfg' | xargs dos2unix
