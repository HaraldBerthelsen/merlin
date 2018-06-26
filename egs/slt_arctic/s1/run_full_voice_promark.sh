#!/bin/bash -e

if test "$#" -gt 1; then
    echo "Usage: ./run_full_voice_promark.sh (starting step)"
    exit 1
fi
if test "$#" -eq 1; then
    step=$1
else
    step=1
fi

Voice=slt_arctic_full_promark
MerlinDir=~/git/hb_merlin
Labels=state_align


./run_promark.sh $MerlinDir $Voice $Labels $step
