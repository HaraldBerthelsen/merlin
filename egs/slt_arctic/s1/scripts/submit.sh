#!/bin/bash -e
## Generic script for submitting any Theano job to GPU
# usage: submit.sh [scriptname.py script_arguments ... ]

src_dir=$(dirname $1)

# Source install-related environment variables
source ${src_dir}/setup_env.sh

use_gpu_lock=true

if [ "$use_gpu_lock" = true ]; then
    # Try to lock a GPU...
    gpu_id=$(python ${src_dir}/gpu_lock.py --id-to-hog)

    # Run the input command (run_merlin.py) with its arguments
    if [ $gpu_id -gt -1 ]; then
        echo "Running on GPU id=$gpu_id ..."
        #HB THEANO_FLAGS="mode=FAST_RUN,device=gpu$gpu_id,"$MERLIN_THEANO_FLAGS
        THEANO_FLAGS="mode=FAST_RUN,device=cuda$gpu_id,"$MERLIN_THEANO_FLAGS
       export THEANO_FLAGS
    
    { # try  
            python $@
	    #hb
	    RETURNVAL=$?
            python ${src_dir}/gpu_lock.py --free $gpu_id
    } || { # catch   
	    RETURNVAL=1
            python ${src_dir}/gpu_lock.py --free $gpu_id
    }
    else
        echo "No GPU is available! Running on CPU..."

        THEANO_FLAGS=$MERLIN_THEANO_FLAGS
        export THEANO_FLAGS
    
        python $@
	#hb
	RETURNVAL=$?
    fi
else
    # Assign GPU manually...
    gpu_id=0

    # Run the input command (run_merlin.py) with its arguments
    THEANO_FLAGS="mode=FAST_RUN,device=gpu$gpu_id,"$MERLIN_THEANO_FLAGS
    export THEANO_FLAGS
 
    python $@
    RETURNVAL=$?
    exit $RETURNVAL
fi

#hb
#Not sure if this will always cause the calling script to exit..
#anyway works for now - TODO remove if 05 still stops when prom works right
exit $RETURNVAL
